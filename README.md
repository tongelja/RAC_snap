# RacSnap

RacSnap is an Oracle cluster monitoring utility using python3.  You can get a view of all clutser events and statistics.  You also get a view of all sessions running in the cluster and the session statistics for all active sessions.


## Getting Started

To get started, clone the repo:

```
https://github.com/tongelja/RAC_snap.git
```



### Prerequisites

You will need to have cx_Oracle installed.


## Running RacSnap


Run RacSnap with python3 and pass your connection information

```
python3 racsnap.py -c sys/password@SERVER/DB
```

Your output will refresh every few seconds and look like this:

```
| DB Name:      MYDB001
| Open Mode:    READ WRITE
| Current SCN:  1560912527843

- Instance Info -----------
| Instance:     mydb00012                                       | Instance:     mydb00013                                       | Instance:     mydb00014                                       | Instance:     mydb00015
| Host:         myserver00001                                   | Host:         myserver00002                                   | Host:         myserver00003                                   | Host:         myserver00004
| Startup:      2018-03-01 22:35:48                             | Startup:      2018-03-01 22:43:47                             | Startup:      2018-03-01 23:02:42                             | Startup:      2018-03-01 23:21:27
| Inst Status:  OPEN                                            | Inst Status:  OPEN                                            | Inst Status:  OPEN                                            | Inst Status:  OPEN

- Statistics -----------
  Statistic                      Delta           Rate             Statistic                      Delta           Rate             Statistic                      Delta           Rate             Statistic                      Delta           Rate
| physical read bytes            550330K         110066K/Sec    | physical read bytes            61596K          12319K/Sec     | physical read bytes            754385K         150877K/Sec    | cell physical IO bytes eligibl 778633K         155727K/Sec
| physical read total bytes opti 550863K         110173K/Sec    | physical read total bytes opti 62120K          12424K/Sec     | physical read total bytes opti 754819K         150964K/Sec    | physical read bytes            971882K         194376K/Sec
| physical read total bytes      550953K         110191K/Sec    | physical read total bytes      62153K          12431K/Sec     | physical read total bytes      754876K         150975K/Sec    | physical read total bytes opti 972587K         194517K/Sec
| cell physical IO interconnect  613036K         122607K/Sec    | cell physical IO interconnect  63786K          12757K/Sec     | cell physical IO interconnect  761354K         152271K/Sec    | physical read total bytes      973660K         194732K/Sec
| logical read bytes from cache  38769M          7754M/Sec      | logical read bytes from cache  1681M           336119K/Sec    | logical read bytes from cache  39464M          7893M/Sec      | logical read bytes from cache  15715M          3143M/Sec

- Events -----------
  Event                          Delta (ms)      Rate             Event                          Delta (ms)      Rate             Event                          Delta (ms)      Rate             Event                          Delta (ms)      Rate
| cell multiblock physical read  251301          50260/Sec      | LGWR all worker groups         41007           8201/Sec       | enq: IV -  contention          81101           16220/Sec      | log file parallel write        82300           16460/Sec
| buffer deadlock                496200          99240/Sec      | enq: IV -  contention          44306           8861/Sec       | buffer deadlock                99281           19856/Sec      | buffer deadlock                99327           19865/Sec
| cell list of blocks physical r 2633K           526521/Sec     | log file parallel write        47431           9486/Sec       | cell multiblock physical read  106403          21281/Sec      | cell smart table scan          294393          58879/Sec
| resmgr:cpu quantum             4405K           880941/Sec     | gc current grant busy          59784           11957/Sec      | cell single block physical rea 2623K           524529/Sec     | cell single block physical rea 892208          178442/Sec
| cell single block physical rea 14710K          2942K/Sec      | cell single block physical rea 3160K           632047/Sec     | cell list of blocks physical r 6579K           1316K/Sec      | cell list of blocks physical r 1512K           302464/Sec

- Top Global Sessions (31)-----------
Instance SID,Serial        Username             SQL ID          Event                                             ET     Blk Gets    Cons Gets      Phy Rds     Blk Chgs    Cons Chgs     OS PID  Blocker   QC SID
4        800,13701         MYUSER_1801          2nrsrksxkyh8b   On CPU (Prev: cell smart table scan)               0       143071     26932568      2165656       223724     26932568     302057        0
1        803,38739         MYUSER_1801          0uj4d205y94jf   resmgr:cpu quantum  (scheduler)                    0          999        19170         2759         1277        19170      84541        0
1        996,40299         MYUSER_1801_TM       2x040zk9xb1xj   On CPU (Prev: SQL*Net message to client)           0          208        19799          832          235        19799      59659        0
1        1174,34988        MYUSER_1801          7svjupsxr330g   resmgr:cpu quantum  (scheduler)                    0       246108     66602018      4071764       383843     66602018     385751        0
4        1188,48070        SYS                  1bd9cdacpu3nq   On CPU (Prev: PX Deq: Execution Msg)               0            0            0            0            0            0     175733        0       80
2        1190,46289        SYS                  1bd9cdacpu3nq   On CPU (Prev: PX Deq: Execution Msg)               0            0            0            0            0            0     158226        0       80
2        1215,3825         MYUSER_1801          gbz92jpb6rpzs   cell single block read request  (user...           0       261872     61835926      3309244       405273     61835926     242362        0
3        1227,14285        SYS                  1bd9cdacpu3nq   On CPU (Prev: PX Deq: Execution Msg)               0            0            0            0            0            0     250202        0       80
3        1235,42002        MYUSER_1801_TM       1y0r3szbz8sg7   cell list of blocks read request  (us...           0          194         4627          467          220         4627     222508        0
1        1372,18382        SYS                  1bd9cdacpu3nq   On CPU (Prev: PX Deq: Execution Msg)               0            0            0            0            0            0        426        0       80
1        252,52574         MYUSER_1801          dp76nnpnk5x12   On CPU (Prev: cell single block physica...)        1         1808        64288         9909         3455        64288      84047        0
3        476,6393          MYUSER_1801          --              Streams AQ: waiting for messages in t...           1        13765        31630          212        16789        31630     335294        0
4        16,7601           MYUSER_1801          0nq6g9pajvmpf   cell list of blocks read request  (us...           3       300541     72989509      3953346       465652     72989509     241973        0
1        624,16464         MYUSER_1801          0nq6g9pajvmpf   On CPU (Prev: resmgr:cpu quantum)                  9       325065     75249913      2898398       498439     75249913       9658        0
3        451,63524         MYUSER_1801          5u2v8ah38ymmy   cell list of blocks read request  (us...         214       551059    138626617      5469015       845383    138626617     123694        0
1        1364,17139        MYUSER_1801          0uj4d205y94jf   cell single block read request  (user...         656       105559      6053459      1645835       172593      6053459      22426        0
1        1011,49177        MYUSER_1801          d6s8ckcvn1rj2   On CPU (Prev: cell list of blocks physi...)      698       180636     70632078      3003582       280997     70632078      17716        0
3        66,61673          MYUSER_1801          --              gc cr request  (cluster)                       12129      2262445    526802472     27997417      3452994    526802472     290118        0
1        418,51737         SYS                  --              class slave wait  (idle)                      976963            0            0            0            0            0      60129        0
1        1373,9678         SYS                  --              class slave wait  (idle)                      976963            0            0            0            0            0      60163        0
1        1380,6824         SYS                  --              class slave wait  (idle)                      977303            0            0            0            0            0      16818        0
1        250,28735         SYS                  --              class slave wait  (idle)                      977321            0            0            0            0            0      14016        0
1        256,23772         SYS                  --              class slave wait  (idle)                      977321            0            0            0            0            0      14010        0
1        1173,50765        SYS                  --              class slave wait  (idle)                     1246448            0            0            0            0            0     384372        0
1        797,8137          SYS                  --              class slave wait  (idle)                     1246489            0            0            0            0            0     381489        0
1        411,24122         SYS                  --              class slave wait  (idle)                     1252292            0            0            0            0            0      70605        0
4        1158,46088        SYS                  --              class slave wait  (idle)                     1269151            0            0            0            0            0     177622        0
3        1158,59998        SYS                  --              class slave wait  (idle)                     1270271            0            0            0            0            0     267865        0
2        1158,24444        SYS                  --              class slave wait  (idle)                     1271406            0            0            0            0            0     160907        0
1        780,47308         SYS                  --              class slave wait  (idle)                     1271876            0            0            0            0            0       5696        0

```




## Authors

* **John Tongelidis** - *Initial work* - [tongelja](https://github.com/tongelja)
