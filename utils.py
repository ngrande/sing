def print_elapsed_time(start_time, end_time):
    '''From seconds to Days;Hours:Minutes;Seconds
    http://stackoverflow.com/a/29626289/3645029'''

    diff = end_time - start_time
    valueD = (((diff/365)/24)/60)
    Days = int(valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = int(valueS)

    print('{0!s} day(s); {1:02}:{2:02}:{3:02}'
          .format(Days, Hours, Minutes, Seconds))
