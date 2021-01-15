# RISK
from scripts.constants.configs import HOME, AWAY
from scripts.constants.league import *

HIGH_RISK = 'high_risk'
LOW_RISK = 'low_risk'


SERIA_A_CONFIG = {LOW_RISK: {HOME: {'thr': 0.55,
                                    'filter_bet': 1.05},

                             AWAY: {'thr': 0.75,
                                    'filter_bet': 1.15}
                             },

                  HIGH_RISK: {HOME: {'thr': 0.5,
                                     'filter_bet': 1.20},

                              AWAY: {'thr': 0.55,
                                     'filter_bet': 1.1}
                              }
                  }

PREMIER_CONFIG = {LOW_RISK: {HOME: {'thr': 0.65,
                                    'filter_bet': 1.05},
                             AWAY: {'thr': 0.65,
                                    'filter_bet': 1.2},
                             },

                  HIGH_RISK: {HOME: {'thr': 0.7,
                                    'filter_bet': 1.05},
                              AWAY: {'thr': 0.6,
                                    'filter_bet': 1.2},

                             }
                  }

# UPDATE: MAX 2 ROUND
LIGUE_1_CONFIG = {LOW_RISK: {HOME: {'thr': 0.5,
                                    'filter_bet': 1.2},
                             AWAY: {'thr': 0,
                                    'filter_bet': 0},
                             },

                  HIGH_RISK: {HOME: {'thr': 0.6,
                                    'filter_bet': 1.2},
                              AWAY: {'thr': 0.7,
                                    'filter_bet': 1.2},

                             }
                  }

EREDIVISIE_CONFIG = {LOW_RISK: {HOME: {'thr': 0.5,
                                    'filter_bet': 1.05},
                                AWAY: {'thr': 0.5,
                                    'filter_bet': 1.2},
                                },

                    HIGH_RISK: {HOME: {'thr': 0.7,
                                    'filter_bet': 1.15},
                                AWAY: {'thr': 0.7,
                                    'filter_bet': 1.15},

                               }
                  }

JUPILIER_CONFIG = {LOW_RISK: {HOME: {'thr': 0.5,
                                     'filter_bet': 1.05},
                              AWAY: {'thr': 0.5,
                                     'filter_bet': 1.2},
                              'combo': 'x2'
                                },

                    HIGH_RISK: {HOME: {'thr': 0.7,
                                    'filter_bet': 1.10},
                                AWAY: {'thr': 0.7,
                                    'filter_bet': 1.15},
                                'combo': 'x2'
                               }
                  }

LIGA_CONFIG = {LOW_RISK: {HOME: {'thr': 0.5,
                                     'filter_bet': 1.05},
                              AWAY: {'thr': 0.5,
                                     'filter_bet': 1.2},
                              'combo': 'x2'
                                },

                    HIGH_RISK: {HOME: {'thr': 0.7,
                                    'filter_bet': 1.10},
                                AWAY: {'thr': 0.7,
                                    'filter_bet': 1.15},
                                'combo': 'x2'
                               }
                  }

LIGA_2_CONFIG = {LOW_RISK: {HOME: {'thr': 0.5,
                                     'filter_bet': 1.05},
                              AWAY: {'thr': 0.5,
                                     'filter_bet': 1.2},
                              'combo': 'x2'
                                },

                    HIGH_RISK: {HOME: {'thr': 0.5,
                                    'filter_bet': 1.05},
                                AWAY: {'thr': 0.7,
                                    'filter_bet': 1.15},
                                'combo': 'x2'
                               }
                  }



PREDICT_CONFIG = {SERIE_A: SERIA_A_CONFIG,
                  PREMIER: PREMIER_CONFIG,
                  LIGUE_1: LIGUE_1_CONFIG,
                  EREDIVISIE: EREDIVISIE_CONFIG,
                  JUPILIER: JUPILIER_CONFIG}
