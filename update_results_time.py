#!/usr/bin/python
# -*- coding: utf-8 -*-

def update_results_time(connection, exp_id):
    cursor = connection.cursor()
    
    cursor.execute("SELECT experiment_id, min(time) from video WHERE experiment_id = %s GROUP BY experiment_id", exp_id)
    row = cursor.fetchone()
    min_time = row[1]
    cursor.execute("UPDATE results r, results_directory rd SET distance_from_origin = hour(timediff(mid(time, 13), mid(%s, 13) )) * 3600 + minute(timediff(mid(time, 13), mid(%s, 13) ))*60 + SECOND( timediff(mid(time, 13), mid(%s, 13) )) + microsecond( timediff(mid(time, 13), mid(%s, 13) ))/1000000.0 where rd.experiment_id = %s and r.result_id = rd.id",     (min_time, min_time, min_time, min_time, exp_id))
 
