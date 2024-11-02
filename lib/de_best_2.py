import numpy as np

class DE_Best_2:

    def __init__(self, ps, length_b1_b2, length_b1_b3, ps1, ps2):
        # Definisi parameter untuk Differential Evolution
        # ------------------------------
        self.pop_size = 2000 # size population candidate solution
        self.iter = 50  # number iteration

        self.F = 0.02     # scale factor [0, 1]
        self.CR = 0.8    # crossover rate [0, 2]

        self.n = 10  # number compressor
        self.m = self.n + 1 # number pipe
        self.N1 = 4  # number compressor in branch 1
        self.N2 = 3  # number compressor in branch 2
        self.N3 = 3  # number compressor in branch 3

        self.ps = ps
        self.length_b1_b2 = length_b1_b2
        self.length_b1_b3 = length_b1_b3
        self.ps1 = ps1
        self.ps2 = ps2

        # Definisi batas atas dan batas bawah untuk setiap dimensi pipe
        # pipe = [pd, ps, l, d]

        # Bounds for branch 1
        self.bounds1 = np.asarray([
            (590, 1000),(300, 900),(2, 70),(4, 36)
        ])
        # Bounds for branch 2
        self.bounds2 = np.asarray([
            (590, 1000),(300, 900),(2, 30),(4, 18)
        ])
        # Bounds for branch 3
        self.bounds3 = np.asarray([
            (590, 1000),(200, 860),(2, 70),(4, 18)
        ])

        best_b1_b2 = self.get_best_b1_b2()
        best_b1_b3 = self.get_best_b1_b3()

        # Best vector untuk pipe di branch 1, branch 2, dan branch 3
        self.best_all = np.concatenate((best_b1_b2[0], best_b1_b3[0][3:]))
        self.K = self.get_k()
    
    def get_k(self):
        # TODO 1. Hitung K
        K = []

        for i in range(len(self.best_all)-1):
            if i == 0: K.append(self.best_all[i][0]/self.ps)
            else: K.append(self.best_all[i][0]/self.best_all[i-1][1])

        return K

    def get_best_b1(self):
        # Mengambil vector pipe pada branch 1 yang akan digunakan untuk evaluasi
        best_b1_b2 = self.get_best_b1_b2()
        demand1_index = 0
        for i in range(len(best_b1_b2[0])):
            if round(best_b1_b2[0][i][1]) == self.ps1:
                demand1_index = i
        best_b1 = []
        for p in best_b1_b2[0]:
            if(round(p[1]) != self.ps1):
                best_b1.append(p)
            if len(best_b1) == self.N1 - 1:
                break
        return best_b1
    
    # Fungsi untuk mengolah populasi awal pipa dari branch 1 dan branch 3 yang hanya memenuhi panjang total
    # Input : populasi awal pipe branch 1 + branch 3, ukuran populasi, N1, dan N3
    # Output : vector populasi awal yang memenuhi panjang dari branch 1 dan branch 3
    def get_pipe_length2(self, pipe_b3):
        best_pipe = []
        for i in range(self.pop_size): # 1, 2, ..., 50
            temp = []
            sum_pipe = 0
            for j in range(self.N1 + self.N3): # 1, 2, 3, 4, 5, 6, 7
                if j < self.N1-1: # 0, 1, 2
                    sum_pipe += self.best_b1[j][2]
                if j >= self.N1-1: # 3, 4, 5, 6 => 0, 1, 2, 3
                    sum_pipe += pipe_b3[j-self.N3][i][2]
                    temp.append(pipe_b3[j-self.N3][i])
            if(round(sum_pipe) == self.length_b1_b3):
                best_pipe.append(temp)
        return best_pipe
    
    # Proses inisialisasi populasi awal setiap pipe pada branch 3
    # <-----Branch 1-----> <--------Branch 3----------->
    # pipe1, pipe2, pipe3, pipe8, pipe9, pipe10, pipe11,
    def create_pipe_b3(self):
        while True:
            # Initialize population pipe branch 3
            pipe_b3 = []
            for i in range(self.N3 + 1):
                pipe_b3.append(self.bounds3[:, 0] + (np.random.rand(self.pop_size, len(self.bounds3)) * (self.bounds3[:, 1] - self.bounds3[:, 0])))
            best_pipe_b3 = self.get_pipe_length2(pipe_b3)
            if(best_pipe_b3 != [] and len(best_pipe_b3) > 4):
                break
        return best_pipe_b3
    
    def diff_evol_2(self, pop_pipe_b3, best_b1, pop_size):

        # Check inequality branch 3
        pop_pipe = [self.check_inequality(p) for p in pop_pipe_b3]
        pop_pipe = np.array(pop_pipe)

        # Evaluate initial population candidate solution
        temp = [np.concatenate((best_b1, p)) for p in pop_pipe_b3]
        obj_all = [self.f(p, self.N1 + self.N3, self.N1 + self.N3) for p in temp]

        # Find the best vector of initial population
        best_vector = pop_pipe[np.argmin(obj_all)]
        best_obj = min(obj_all)
        prev_obj = best_obj

        for i in range(self.iter):
            # Iterate over all candidate solution
            for j in range(pop_size):
                # MUTATION
                while(True):
                    # Choose 3 candidate solution : a, b, c.
                    # Xbest, X1, X2
                    a = pop_pipe[np.argmin(obj_all)]
                    # Choose 5 candidate solution : a, b, c, d, e
                    candidates = [candidate for candidate in range(pop_size) if candidate != j]
                    b, c, d, e = pop_pipe[np.random.choice(candidates, 4, replace=False)]
                    # Perform mutation
                    mutated = self.mutation([a, b, c, d, e], self.F)
                    # Check bound mutated vector
                    mutated = self.check_bounds(mutated, self.bounds3)
                    # Check inequality const
                    mutated = self.check_inequality(mutated)
                    # Check lenght, if true continue, else LOOP UNTIL
                    temp = np.concatenate((best_b1, mutated))
                    if self.check_length2(temp):
                        break
                # CROSSOVER
                # Perform crossover
                while(True):
                    mutated_temp = np.concatenate((best_b1, mutated))
                    target_temp = np.concatenate((best_b1, pop_pipe[j]))
                    trial = np.array(self.crossover(mutated_temp, target_temp, self.N1 + self.N3, self.CR))
                    if self.check_length2(trial):
                        break

                # Compute objective function value for target vector]
                obj_target = self.f(target_temp, self.N1 + self.N3, self.N1 + self.N3)
                # Compute objective function value for trial vector
                obj_trial = self.f(trial, self.N1 + self.N3, self.N1 + self.N3)

                # SELECTION
                # Perform selection
                if obj_trial < obj_target:
                    # Replace target vector with trial vector
                    pop_pipe[j] = trial[3:]
                    # Store the new obj function value
                    obj_all[j] = obj_trial

            # Find best performing vector each iteration
            best_obj = min(obj_all)
            # Store the lowest obj function value
            if best_obj < prev_obj:
                best_vector = pop_pipe[np.argmin(obj_all)]
                prev_obj = best_obj

        #     # Print progress iteration
        #     # print('Iteration %d : f[%s] = %.5f' % (i, np.around(best_vector, decimals=5), best_obj))
        #     # print('--------------------')
        best_vector = np.concatenate((best_b1, best_vector))
        return [best_vector, best_obj]
    
    def get_best_b1_b3(self):
        best_b1 = self.get_best_b1()
        while(True):
            best_pipe_b3 = self.create_pipe_b3()
            best_b1_b3 = self.diff_evol_2(best_pipe_b3, best_b1, len(best_pipe_b3))
            status = False
            if(round(best_b1_b3[0][self.N1 + self.N3 - 1][1]) == self.ps2):
                status = True
            if status and (best_b1_b3[0][:3] == best_b1).all() and self.check_inequality_2(best_b1_b3[0][:3]):
                break
    
    def get_best_b1_b2(self):
        # Proses Differential Evolution hingga memenuhi setiap constraint
        # Hingga memenuhi Ps demand 1 = 600 psi
        best_pipe_b1_b2 = self.get_best_pipe_b1_b2()
        while(True):
            best_b1_b2 = self.diff_evol1(best_pipe_b1_b2, len(best_pipe_b1_b2));
            status = False
            if(round(best_b1_b2[0][self.N1 + self.N2-1][1]) == self.ps1 and self.check_inequality_2(best_b1_b2[0])):
                break

        return best_b1_b2

    def get_best_pipe_b1_b2(self):
        # Proses inisialisasi populasi awal setiap pipe pada branch 1 dan branch 2
        # <-----Branch 1-----> <--------Branch 2--------->
        # pipe1, pipe2, pipe3, pipe4, pipe5, pipe6, pipe7,

        while True:
            # Initialize population pipe branch 1
            pipe_b1 = []
            for i in range(self.N1 - 1):
                pipe_b1.append(self.bounds1[:, 0] + (np.random.rand(self.pop_size, len(self.bounds1)) * (self.bounds1[:, 1] - self.bounds1[:, 0])))
            # Initialize population pipe branch 2
            pipe_b2 = []
            for i in range(self.N2+1):
                pipe_b2.append(self.bounds2[:, 0] + (np.random.rand(self.pop_size, len(self.bounds2)) * (self.bounds2[:, 1] - self.bounds2[:, 0])))
            # Concatenate population pipe branch 1 and branch 2
            pipe_b1_b2 = np.concatenate((pipe_b1, pipe_b2))
            # Get all pipes whichs meet constraint length branch 1 and branch 2
            best_pipe_b1_b2 = self.get_pipe_length1(pipe_b1_b2)
            if(best_pipe_b1_b2 != []):
                break
        
        return best_pipe_b1_b2

    # Fungsi differential evolution untuk pipe branch 1 dan branch 2
    def diff_evol1(self, pop_pipe, pop_size):

        # Check inequality
        pop_pipe = [self.check_inequality(p) for p in pop_pipe]
        pop_pipe = np.array(pop_pipe)

        # Evaluate initial population candidate solution
        obj_all = [self.f(p, self.N1 + self.N2, self.N1 + self.N2) for p in pop_pipe]

        # Find the best vector of initial population
        best_vector = pop_pipe[np.argmin(obj_all)]
        best_obj = min(obj_all)
        prev_obj = best_obj

        for i in range(self.iter):
            # Iterate over all candidate solution
            for j in range(pop_size):
                # MUTATION
                while(True):
                    # Choose 3 candidate solution : a, b, c.
                    # Xbest, X1, X2
                    a = pop_pipe[np.argmin(obj_all)]
                    # Choose 5 candidate solution : a, b, c, d, e
                    candidates = [candidate for candidate in range(pop_size) if candidate != j]
                    b, c, d, e = pop_pipe[np.random.choice(candidates, 4, replace=False)]
                    # Perform mutation
                    mutated = self.mutation([a, b, c, d, e], self.F)
                    # Check bound mutated vector
                    mutated_b1 = self.check_bounds(mutated[:3], self.bounds1)
                    mutated_b2 = self.check_bounds(mutated[3:], self.bounds2)
                    mutated = np.concatenate((mutated_b1, mutated_b2))
                    # Check inequality const
                    mutated = self.check_inequality(mutated)
                        # Check lenght, if true continue, else LOOP UNTIL
                    if self.check_length1(mutated):
                        break

                # CROSSOVER
                # Perform crossover
                while(True):
                    trial = np.array(self.crossover(mutated, pop_pipe[j], self.N1 + self.N2, self.CR))
                    if self.check_length1(trial):
                        break

                # Compute objective function value for target vector
                obj_target = self.f(pop_pipe[j], self.N1 + self.N2, self.N1 + self.N2)
                # Compute objective function value for trial vector
                obj_trial = self.f(trial, self.N1 + self.N2, self.N1 + self.N2)

                # SELECTION
                # Perform selection
                if obj_trial < obj_target:
                    # Replace target vector with trial vector
                    pop_pipe[j] = trial
                # Store the new obj function value
                obj_all[j] = obj_trial

            # Find best performing vector each iteration
            best_obj = min(obj_all)
            # Store the lowest obj function value
            if best_obj < prev_obj:
                best_vector = pop_pipe[np.argmin(obj_all)]
                prev_obj = best_obj

            # Print progress iteration
            # print('Iteration %d : f[%s] = %.5f' % (i, np.around(best_vector, decimals=5), best_obj))
            # print('--------------------')

        return [best_vector, best_obj]

    # Fungsi untuk mengolah populasi awal pipa dari branch 1 dan branch 2 yang hanya memenuhi panjang total
    # Input : populasi awal pipe branch 1 + branch 2, ukuran populasi, N1, dan N2
    # Output : vector populasi awal yang memenuhi panjang dari branch 1 dan branch 2
    def get_pipe_length1(self, pipe_b1_b2):
        best_pipe = []
        for i in range(self.pop_size): # 1, 2, ..., 1000
            temp = []
            sum_pipe = 0
            for j in range(self.N1 + self.N2): # 1, 2, 3, 4, 5, 6, 7
                sum_pipe += pipe_b1_b2[j][i][2]
                temp.append(pipe_b1_b2[j][i])
            if(round(sum_pipe) == self.length_b1_b2):
                best_pipe.append(temp)
        return best_pipe

    # Fungsi Q untuk menghitung Flow Rate
    # Input : pd, ps, L, D
    # Output : Q
    def q(pd, ps, l, d):
        return (871 * ((d)**(8/3))) * np.sqrt((pd**2 - ps**2) / l)
    
    # Objective Function F()
    # x = [pd, ps, l, d]

    # Fungsi objektif untuk operating cost compressor
    def f_comp(x, q, co = 8, cc = 70.00, T = 520, k = 1.26, z = 0.9):
        return ((co + cc) * q * 0.08531 * T * (k/(k - 1)) * ((x[0]/x[1])**((z*(k - 1))/k) - 1))
    # Fungsi objektif untuk maintenance cost pipe
    def f_pipe(x, cs = 870):
        return (cs * x[2] * x[3])

    # Fungsi objektif
    # Input: 1 set pipe (pipe1, pipe2, ..., pipei), jumlah compressor, jumlah pipe
    # Output: sum fungsi objektif
    def f(self, pop, n, m):
        sum = 0
        for i in range(n):
            qi = self.q(pop[i][0],pop[i][1],pop[i][2],pop[i][3])/1000000
        sum += self.f_comp(pop[i], qi)
        for j in range(m):
            sum += self.f_pipe(pop[j])
        return sum

    # Fungsi untuk Mutation
    # Input : target pipe dan F
    # Output : mutated vector
    def mutation(x, F):
        return np.add(x[0], np.multiply(F, np.add(np.subtract(x[1], x[2]), np.subtract(x[3], x[4]))))
    
    # Fungsi untuk Crossover
    # Input : mutated vector, target pipe, dimensi dari pipe = 7, dan CR
    # Output : trial vector
    def crossover(mutated, target, dims, cr):
        # Generate uniform random value untuk setiap dimension
        p = np.random.rand(dims)
        # Generate Trial Vector dari binomial crossover
        trial = [mutated[i] if p[i] < cr else target[i] for i in range(dims)]
        return trial
    
    # Fungsi untuk mengecek batasan dari pd, ps, L, D pada tiap pipe dari 1 set pipe
    # Input : mutated pipe dan batasan
    # Output : mutated pipe yang memenuhi batasan
    def check_bounds(mutated, bounds):
        mutated_bound = []
        for i in range(len(mutated)):
            temp = []
            for j in range(len(bounds)):
                temp.append(np.clip(mutated[i][j], bounds[j, 0], bounds[j, -1]))
            mutated_bound.append(temp)
        return mutated_bound
    
    # Fungsi untuk cek constraint pertidaksamaan
    # 1.) Pd/Ps >= 1
    # 2.) Pd/Ps <= Ki
    # 3.) Flow rate kuadrat = 0
    # Input : target pipe
    # Output : pipe yang memenuhi constraint
    def check_inequality(pop, K=[]):
        # Cek Pd >= Ps
        for p in pop:
            if p[0] <= p[1]:
                p[0],p[1] = p[1],p[0]
        # Cek K
        # Cek Q
        return pop
    def check_inequality_2(self, pop):
        for i in range(len(pop)):
            if i == 0:
                if (pop[i][0]/self.ps) < 1:
                    return False
            else:
                if (pop[i][0]/pop[i-1][1]) < 1:
                    return False
        return True
    
    # Fungsi untuk cek total panjang dari branch 1 dan branch 2
    def check_length1(self, pop):
        return True if round(sum(pop[:,2])) == self.length_b1_b2 else False
    # Fungsi untuk cek total panjang dari branch 1 dan branch 3
    def check_length2(self, pop):
        return True if round(sum(pop[:,2])) == self.length_b1_b3 else False
    
