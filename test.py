import numpy as np
from typing import List

object_var = [[701.25133261,471.00881617,  21.52499159,4.        ]
,[971.80988514,476.26989277,  43.71686891,13.17587302]
,[635.69332774,568.92785319,60.13303615, 4.07253664]
,[723.8564513,  626.48684081,20.69870245,4.08411964]
,[769.47972613,609.95056145,6.20970002, 18.        ]
,[760.93590527,614.84791113,12.45646561,7.11428831]
,[640.44483082,600.18795116,10.17975685,13.6550791,]
,[844.06634243,580.5532022,37.18612387,5.42823829]
,[739.4223457,342.03999175,7.81809052,4.34848526]
,[997.73933601,376.8800504,13.78066334,8.86298738]
,[979.5699358,299.88804521,15.55203021,10.84434546]]

try:
    keys = ["ps", "pd", "l", "d"]
    data = [dict(zip(keys, sublist)) for sublist in object_var]
    # data = dict(object_var)
    print(data)
except Exception as e:
    errors: List[Exception] = []
    errors.append(e)
    try:
        data = vars(object_var)
    except Exception as e:
        errors.append(e)
        raise ValueError(errors) from e
