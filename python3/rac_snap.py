#!/bin/python

#use this executable to run /tools/python/virtual/dba/bin/python

##########################
##
##
##
##
##################################


###########################
##
## Import
###
#####################################

import os, re, sys, getopt, operator, time, cx_Oracle, getpass
sys.path.append(os.path.abspath('bin'))
import orautility


##############################
##
## Functions
##
#######################################

##
## usage
##
def usage_exit(message):
    print(message)
    print("Usage:")
    print(os.path.abspath( __file__ ), '\n \
    Options: \n\n \
        [ -c CONNECTION_STRING ] \n \
             Connection String Format:  SID:Hostname[:User:Password] \n\n \
        [ -f SNAPSHOT[:LINES],... ] \n \
             Snapshot Options: GSESS \n \
                               SESS \n \
                               STAT \n \
                               EVENT \n \
                               METRIC \n ')

    sys.exit(2)


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def max_length(a, b):
    c = len(str(a))
    d = len(str(b))
    if c > d:       return a
    else:           return b


##
## main
##
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:f:")
    except getopt.GetoptError as err:
        print(str(err))
        usage_exit('getopt error:')

    connect    = None
    format     = None
    ORACLE_SID = None

    for o, a in opts:
        if o in ('-c'):
            connect = a
        elif o in ('-f'):
            format = a
        else:
            assert False, "unhandled option"

        
    if format is None:
        format = 'STAT,EVENT,GSESS'

    conn = orautility.createOraConnection(connect)

    my_snap = Instances_Snap(conn, format)

    while 1 == 1:
        try:
            my_snap.create_snapshot()
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)

        
    

   
class Instances_Snap:
 
    def __init__(self, 
                 conn, 
                 display_items):
    
    
        self.delimiter                 = '-----------'
        self.column_format_01          = '%-40s %-2s'
        self.column_format_02          = '%-40s %15s %20s'
        self.column_format_03          = '%-40s %15.1f %15.1f %-4s'
        self.column_format_04          = '%-80s'
        self.linesize                  = 250
 
        self.sleep_time                = 5
        self.db                        = conn
        self.sys                       = {}
        self.display_items             = []

  
        for i in display_items.upper().split(','):
            j = i.split(':')
            self.display_items.append( j[0] )

            if j[0] == 'GSESS':
                if len(j) > 1:       self.print_global_sess_lines = int( j[1] )
                else:                self.print_global_sess_lines = 5
            if j[0] == 'SESS':
                if len(j) > 1:       self.print_sess_lines = int( j[1] )
                else:                self.print_sess_lines = 5
            if j[0] == 'STAT':
                if len(j) > 1:       self.print_stat_lines = int( j[1] )
                else:                self.print_stat_lines = 5
            if j[0] == 'EVENT':
                if len(j) > 1:       self.print_event_lines = int( j[1] )
                else:                self.print_event_lines = 5
            if j[0] == 'METRIC':
                if len(j) > 1:       self.print_event_lines = int( j[1] )
                else:                self.print_event_lines = 5

    
    def create_snapshot(self):

        self.snapshot_switch = { 
                                'STAT':    self.get_stats_snapshot,
                                'EVENT':   self.get_events_snapshot,
                                'GSESS':   self.get_global_sess_snapshot,
                               }

        self.print_switch = {   
                                 'STAT':    self.print_stats, 
                                 'EVENT':   self.print_events, 
                                 'GSESS':   self.print_global_sessions, 
                            }


        for i in self.display_items:
            self.snapshot_switch[i](1)
    
        time.sleep(self.sleep_time)

        self.get_db_info()

        for i in self.display_items:
            self.snapshot_switch[i](2)

 
        os.system('clear')
    
        self.print_db_info()             
        for i in self.display_items:
            self.print_switch[i]()


    def get_db_info(self):
   
        cursor             = self.db.cursor()
        self.sys['db']                 = {}
        self.sys['instances']          = {}
        self.sys['instance_count']     = {}


        fields = "instance_name, regexp_substr(host_name, '[[:alnum:]]?*', 1), version, startup_time, status, database_status, sysdate"
        sql_stmt = "select " + fields + "  from gv$instance order by inst_id"
        cursor.execute(sql_stmt)
        rows = cursor.fetchall()
       
        fields = 'instance_name, host_name, version, startup_time, status, database_status, sysdate'
        field_list = fields.split(',')
        r = []
        for row_num in range(0, len(rows)):
            r.append( {} )
            for i in range(0, len(field_list) ):
                r[row_num][ field_list[i].strip() ] = rows[row_num][i]
        self.sys['instances'] = r

        fields = 'dbid, name, checkpoint_change#, archive_change#, controlfile_sequence#, open_mode, current_scn '
        sql_stmt = "select " + fields + "  from v$database"
        cursor.execute(sql_stmt)
        rows = cursor.fetchall()

        field_list = fields.split(',')
        r = []
        for row_num in range(0, len(rows)):
            r.append( {} )
            for i in range(0, len(field_list) ):
                r[row_num][ field_list[i].strip() ] = rows[row_num][i]
        self.sys['db'] = r


        sql_stmt = "select count(*)  from gv$instance"
        cursor.execute(sql_stmt)
        rows = cursor.fetchall()

        #for row_num in range(0, len(rows)):
        #    for i in range(0, len(field_list) ):
        r = rows[0][0]

        self.sys['instance_count'] = r



    def get_stats_snapshot(self, run):
        cursor     = self.db.cursor()
        sql_stmt   = "select statistic#, name, value, inst_id from gv$sysstat order by inst_id, statistic# "

        if run == 1:
            cursor.execute(sql_stmt)
            rows = cursor.fetchall()

            self.sys['stat']         = {}
            node_stats               = {}
            node_stats['delta']      = []
            node_stats['run_data']   = {}

            for i in range(0, len(rows)):
                name    = rows[i][1]
                value   = rows[i][2]
                inst_id = rows[i][3]
                
                if not inst_id in self.sys['stat']:
                    self.sys['stat'][inst_id] = {}
                    self.sys['stat'][inst_id]['run_data'] = {}

                self.sys['stat'][inst_id]['run_data'][name]              = {}
                self.sys['stat'][inst_id]['run_data'][name]['name']      = name
                self.sys['stat'][inst_id]['run_data'][name]['inst_id']   = inst_id 
                self.sys['stat'][inst_id]['run_data'][name]['run_01']    = value

        if run == 2:
            d = {}
            l = []

            cursor.execute(sql_stmt)
            rows = cursor.fetchall()
            d = {}
            for i in range(0, len(rows)):
                name    = rows[i][1]
                value   = rows[i][2]
                inst_id = rows[i][3]
                
                run01_value= self.sys['stat'][inst_id]['run_data'][name]['run_01']
                self.sys['stat'][inst_id]['run_data'][name]['run_02'] = value
                delta = value - run01_value
                self.sys['stat'][inst_id]['run_data'][name]['delta'] = delta
                if delta > 0:
                    if inst_id in d:
                        d[inst_id][name] = delta
                    else:
                        d[inst_id] = {}
            

            instances = self.sys['instance_count']
            for i in range(1, instances+1):
                l = sorted(iter(d[i].items()), key=operator.itemgetter(1))
                self.sys['stat'][i]['delta'] = l



    def get_global_sess_snapshot(self, run):

        if run == 1:
            pass

        elif run == 2:
            cursor               = self.db.cursor()
            self.sys['glob_sess']     = []

            sql_stmt = "select  s.state, \
                        s.sid || ',' || s.serial# sid , \
                        s.username  username, \
                        case when s.state != 'WAITING' \
                             then 'On CPU (Prev: ' || case when length(s.event) > 25 \
                                                      then  rpad(s.event, 25, ' ') || '...)' \
                                                      else s.event || ')' end \
                             else  rpad(s.event || '  (' || lower(s.wait_class) || ')' , 37, ' ') || \
                        case when length(s.event || s.wait_class ) > 35 then '...' else NULL end end as event, \
                        nvl(s.p1text, 'p1') || ': ' || s.p1 p1, \
                        nvl(s.p2text, 'p2') || ': ' || s.p2 p2, \
                        nvl(s.p3text, 'p3') || ': ' || s.p3 p3 , \
                        nvl(s.blocking_session, 0) blocking_session, \
                        s.seconds_in_wait seconds, nvl(s.sql_id, '--') sql_id, \
                        s.last_call_et, \
                        io.block_gets, io.consistent_gets, io.physical_reads, io.block_changes, io.consistent_gets, \
                        p.spid, nvl(to_char(px.qcsid), ' '),  \
                        s.inst_id  \
                        from gv$session s, gv$sess_io io, gv$process p, gv$px_session px \
                        where s.inst_id = p.inst_id and s.inst_id = io.inst_id and s.inst_id = px.inst_id(+)  \
                        and p.inst_id = io.inst_id and p.inst_id = px.inst_id  \
                        and io.inst_id = px.inst_id  \
                        and s.sid = px.sid(+) and s.sid = io.sid and  s.paddr = p.addr and s.username is not null \
                        and s.event not like '%rdbms ipc message%' and s.event not like '%message from client%' \
                        and s.status = 'ACTIVE' \
                        order by s.last_call_et, s.sid "

            #print sql_stmt
            cursor.execute(sql_stmt)
            rows = cursor.fetchall()

            r = []
            for i in range(0, len(rows)):
                r.append([])
                r[i] = {}
                r[i]['state']           = rows[i][0]
                r[i]['sid']             = rows[i][1]
                r[i]['username']        = rows[i][2]
                r[i]['event']           = rows[i][3]
                r[i]['p1']              = rows[i][4]
                r[i]['p2']              = rows[i][5]
                r[i]['p3']              = rows[i][6]
                r[i]['blocking_sid']    = rows[i][7]
                r[i]['sec_wait']        = rows[i][8]
                r[i]['sql_id']          = rows[i][9]
                r[i]['last_call_et']    = rows[i][10]
                r[i]['block_gets']      = rows[i][11]
                r[i]['cons_gets']       = rows[i][12]
                r[i]['phy_reads']       = rows[i][13]
                r[i]['blk_changes']     = rows[i][14]
                r[i]['cons_changes']    = rows[i][15]
                r[i]['os_pid']          = rows[i][16]
                r[i]['qc_sid']          = rows[i][17]
                r[i]['instance_id']     = rows[i][18]

            self.sys['glob_sess'] = r


    def get_events_snapshot(self, run):
        cursor     = self.db.cursor()
        sql_stmt = "select event_id, event, time_waited_micro, inst_id from gv$system_event where wait_class not in ('Idle') order by inst_id, event_id"

        if run == 1:
            cursor.execute(sql_stmt)
            rows = cursor.fetchall()

            self.sys['event']        = {}
            node_stats               = {}
            node_stats['delta']      = []
            node_stats['run_data']   = {}

            for i in range(0, len(rows)):
                name    = rows[i][1]
                value   = rows[i][2]
                inst_id = rows[i][3]

                if not inst_id in self.sys['event']:
                    self.sys['event'][inst_id] = {}
                    self.sys['event'][inst_id]['run_data'] = {}

                self.sys['event'][inst_id]['run_data'][name]              = {}
                self.sys['event'][inst_id]['run_data'][name]['name']      = name
                self.sys['event'][inst_id]['run_data'][name]['inst_id']   = inst_id
                self.sys['event'][inst_id]['run_data'][name]['run_01']    = value

        if run == 2:
            d = {}
            l = []

            cursor.execute(sql_stmt)
            rows = cursor.fetchall()
            d = {}
            for i in range(0, len(rows)):
                name    = rows[i][1]
                value   = rows[i][2]
                inst_id = rows[i][3]

                run01_value= self.sys['event'][inst_id]['run_data'][name]['run_01']
                self.sys['event'][inst_id]['run_data'][name]['run_02'] = value
                delta = value - run01_value
                self.sys['event'][inst_id]['run_data'][name]['delta'] = delta
                if delta > 0:
                    if inst_id in d:
                        d[inst_id][name] = delta
                    else:
                        d[inst_id] = {}


            instances = self.sys['instance_count']
            for i in range(1, instances+1):
                l = sorted(iter(d[i].items()), key=operator.itemgetter(1))
                self.sys['event'][i]['delta'] = l


    def print_db_info(self):

        s           = self.sys
        columns     = self.sys['instance_count']
        column_length = self.linesize/columns
        line_format = '{:<' + str(column_length) + '}'


        field_names = { 'instance_name':                     'Instance',
                        'host_name':                         'Host',
                        'startup_time':                      'Startup',
                        'status':                            'Inst Status',
                        'database_status':                   'DB Status',
                        'sysdate':                           'Date',
                        'name':                              'DB Name',
                      }


        i            = 0
        line         = ''
        stat_format  = '{:<13} {:<10}'
        print_fields = ['instance_name', 'host_name', 'sysdate', 'startup_time', 'status', 'database_status']

        print(color.BOLD + '\n-- Instance Info ' + self.delimiter + color.END) 
        for j in print_fields:
            for i in range(0, len(s['instances']) ):
                stat = stat_format.format( field_names[j] + ': ' ,  str(s['instances'][i][j]) )
                line = line + line_format.format( stat )
            print(line)
            line = ''


    def print_stats(self):

        s             = self.sys
        columns       = self.sys['instance_count']
        column_length = self.linesize/columns
        instances     = self.sys['instance_count']
        print_lines   = self.print_stat_lines
        line          = ''
        stat_line     = ''
        head          = ''
        head_line     = ''
        stat_format   = '{:<30} {:<15.0f} {:<15}'
        head_format   = '{:<30} {:<15s} {:<15}'
        line_format = '{:<' + str(column_length) + '}'
        print(color.BOLD + '\n-- Statistics ' + self.delimiter + color.END)
        for line_id in range(print_lines):
            for inst_id in range(1, instances+1):
                i = len( s['stat'][inst_id]['delta']) - line_id -1
                if line_id == 0:
                    head = head_format.format('Statistic (Node: ' + str(inst_id) + ')' , 'Delta', 'Rate')
                    head_line = head_line + line_format.format( head )
                
                statistic = s['stat'][inst_id]['delta'][i][0]
                value     = s['stat'][inst_id]['delta'][i][1]
                delta     = str(s['stat'][inst_id]['delta'][i][1]/self.sleep_time) +  '/Sec' 

                stat_line = stat_format.format( statistic[:30], value, delta )
                line      = line + line_format.format( stat_line )

            if line_id == 0:
                print(color.BOLD + head_line  + color.END)
            print(line) 
            line = ''
            stat_line = ''

    def print_events(self):

        s             = self.sys
        columns       = self.sys['instance_count']
        column_length = self.linesize/columns
        instances     = self.sys['instance_count']
        print_lines   = self.print_event_lines
        line          = ''
        event_line    = ''
        head          = ''
        head_line     = ''
        event_format  = '{:<30} {:<15.0f} {:<15}'
        head_format   = '{:<30} {:<15} {:<15}'
        line_format   = '{:<' + str(column_length) + '}'
        print(color.BOLD + '\n-- Events ' + self.delimiter + color.END)
        for line_id in range(print_lines):
            for inst_id in range(1, instances+1):
                i = len( s['event'][inst_id]['delta']) - line_id -1
                if line_id == 0:
                    head = head_format.format('Event', 'Delta (ms)', 'Rate')
                    head_line = head_line + line_format.format( head )

                if len( s['event'][inst_id]['delta']) <= line_id:
                    event_line = event_format.format( '---', 0, '---')
                    line = line + line_format.format( event_line)
                else:
                    event     = s['event'][inst_id]['delta'][i][0]
                    value     = s['event'][inst_id]['delta'][i][1]
                    delta     = str(s['event'][inst_id]['delta'][i][1]/self.sleep_time) +  '/Sec'

                    event_line = event_format.format( event[:30], value, delta )
                    line      = line + line_format.format( event_line )

            if line_id == 0:
                print(color.BOLD + head_line + color.END)
            print(line)
            line = ''
            event_line = ''


    def print_global_sessions(self):

        print_lines    = self.print_global_sess_lines
        s              = self.sys
        line_format    = '{:<8} {:<17} {:<20} {:<15} {:<43} {:>8} {:>12} {:>12} {:>12} {:>12} {:>12} {:>10} {:>8} {:>8}'
        total_sessions = len(s['glob_sess'])


        if total_sessions > print_lines and print_lines > 0:
            start = total_sessions - print_lines
        else:
            start = 0

        for i in range(start, total_sessions ):

            if i == start:
                print(color.BOLD + '\n-- Top Global Sessions (' + str(total_sessions) + ')' + self.delimiter + color.END)
                line = color.BOLD + line_format.format( 'Instance', 'SID,Serial', 'Username', 'SQL ID', 'Event', 'ET',
                                      'Blk Gets', 'Cons Gets', 'Phy Rds', 'Blk Chgs',
                                      'Cons Chgs', 'OS PID', 'Blocker', 'QC SID' ) + color.END
                print(line)

            line = line_format.format(
                                   s['glob_sess'][i]['instance_id'],
                                   s['glob_sess'][i]['sid'],
                                   s['glob_sess'][i]['username'][:19],
                                   s['glob_sess'][i]['sql_id'],
                                   s['glob_sess'][i]['event'],
                                   s['glob_sess'][i]['last_call_et'],
                                   s['glob_sess'][i]['block_gets'],
                                   s['glob_sess'][i]['cons_gets'],
                                   s['glob_sess'][i]['phy_reads'],
                                   s['glob_sess'][i]['blk_changes'],
                                   s['glob_sess'][i]['cons_changes'],
                                   s['glob_sess'][i]['os_pid'],
                                   s['glob_sess'][i]['blocking_sid'],
                                   s['glob_sess'][i]['qc_sid'] )
            print(line)

#########################
##
## main()
##
##############################
if __name__ == '__main__':
    main()


