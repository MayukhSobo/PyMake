PROTO {
    SC3-00OS04_M2MDT_GP211_JC222_R6,
    SC5-01OS01_GP211_JC302_LTE_TMO,
    S65-85OS04_M2M_GP211_JC222_R6,
    SC5-01OS18_GP221_JC302_LTE_SAT,
    SC5-01OS19_GP221_JC302_LTE_MTN,
}

CODELINE: toolkit

RUN_TEST {
  toolkit
  [
        Toolkit_CompleteBatch: (!*)
        Toolkit_etsi: (!*)
        sat: (!S65-85OS04_M2M_GP211_JC222_R6)
        wib: (SC5-01OS01_GP211_JC302_LTE_TMO, S65-85OS04_M2M_GP211_JC222_R6)
      ]
  browser [
         wib: (SC5-01OS01_GP211_JC302_LTE_TMO, S65-85OS04_M2M_GP211_JC222_R6)
         sat: (!*)
      ]

  framework [

  ]

}

SUMMARY {
    option: yes,
    path: D:\morphoeclipse,
}

WORKSPACE: D:\p4v\ssimbiOS_2_9
PROJECT: SIMbiOS_2_9
