
import numpy as np



test_voltage = {'0': 0.9,
                '1': 0.6,
                '2': 0.6,
                '3': 0.3}


current_specs_ADL = {'15W': {'icc_max':{'VCCCORE':80,
                                    'VCCGT'  :40},
                         'tdc'    :{'VCCCORE':46,
                                    'VCCGT'  :23}},
                 '28W': {'icc_max':{'VCCCORE':80,
                                    'VCCGT'  :40},
                         'tdc'    :{'VCCCORE':47,
                                    'VCCGT'  :23}},
                 '55W': {'icc_max':{'VCCCORE':200,
                                    'VCCGT'  :30},
                         'tdc'    :{'VCCCORE':50, #133,
                                    'VCCGT'  :20}}
                }

current_specs_RPL = {'15W': {'icc_max':{'VCCCORE':76,
                                    'VCCGT'  :40},
                         'tdc'    :{'VCCCORE':46,
                                    'VCCGT'  :23}},
                 '28W': {'icc_max':{'VCCCORE':102,
                                    'VCCGT'  :55},
                         'tdc'    :{'VCCCORE':63,
                                    'VCCGT'  :30}},
                 '55W': {'icc_max':{'VCCCORE':200,
                                    'VCCGT'  :30},
                         'tdc'    :{'VCCCORE':50, #133,
                                    'VCCGT'  :20}}
                }

current_specs_MTL = {'15W': {'icc_max':{'VCCIA':94,
                                    'VCCGT'  :40},
                         'tdc'    :{'VCCIA':46,
                                    'VCCGT'  :23}},
                 '28W': {'icc_max':{'VCCIA':110,
                                    'VCCGT'  :134,
                                    'VCCSA'  :35},
                         'tdc'    :{'VCCIA':61,
                                    'VCCGT'  :30,
                                    'VCCSA'  :28}},
                 '55W': {'icc_max':{'VCCIA':200,
                                    'VCCGT'  :30},
                         'tdc'    :{'VCCIA':50, #133,
                                    'VCCGT'  :20}}
                }

current_specs_LNL = {'8W': {'icc_max':{'VCCIA':47,
                                    'VCCGT'  :61,
                                    'VCCSA' :52},
                         'tdc'    :{'VCCIA' :22,
                                    'VCCGT' :22,
                                    'VCCSA' :22}},
                 '17W': {'icc_max':{'VCCIA' :54,
                                    'VCCGT' :61,
                                    'VCCSA'  :38},
                         'tdc'    :{'VCCIA':26,
                                    'VCCGT'  :22,
                                    'VCCSA'  :22}},
                 '30W': {'icc_max':{'VCCIA':1,
                                    'VCCGT'  :1,
                                    'VCCSA'  :1},
                         'tdc'    :{'VCCIA':1, #133,
                                    'VCCGT'  :1,
                                    'VCCSA' :1}}
                }

current_specs = {'ADL':current_specs_ADL,
                 'RPL':current_specs_RPL,
                 'MTL':current_specs_MTL,
                 'LNL':current_specs_LNL}

loadline_limits_MTL = {"sheet":"Static LL",
                       "cells":{0 :{"current":"P11:P22",
                                     "lower"  :"C11:C22",
                                     "upper"  :"D11:D22"
                                     },
                                1 :{"current":"P41:P52",
                                     "lower"  :"C41:C52",
                                     "upper"  :"D41:D52"
                                     },
                                2 :{"current":"P70:P74",
                                     "lower"  :"C70:C74",
                                     "upper"  :"D70:D74"
                                     }
                                }
                         }

loadline_limits_LNL = {"sheet":"Static LL",
                       "cells":{0 :{"current":"P11:P22",
                                     "lower"  :"C11:C22",
                                     "upper"  :"D11:D22"
                                     },
                                1 :{"current":"P41:P52",
                                     "lower"  :"C41:C52",
                                     "upper"  :"D41:D52"
                                     },
                                2 :{"current":"P70:P74",
                                     "lower"  :"C70:C74",
                                     "upper"  :"D70:D74"
                                     }
                                }
                         }

def test_currents(tdc):
    start_current = 0.1
    end_current = tdc
    num_datapoints =12
    return {'0': np.linspace(start_current,end_current,num_datapoints), 
            '1': np.linspace(start_current,20,num_datapoints),
            '2': [0,2,3,4,5],
            '3': [0,2]}

#def limit_dict(