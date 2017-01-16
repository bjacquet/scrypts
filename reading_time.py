import sys

def words_per_minute():
    return 270

def words_per_second():
    return words_per_minute() / 60

def words_in_text(text):
    return len(text.split())

def reading_time_seconds(word_count):
    return word_count / words_per_second()

def reading_time_minutes(word_count):
    return reading_time_seconds(word_count) / 60

def reading_time(text):
    return reading_time_minutes(words_in_text(text))

def contents(filename):
    file = open(filename, 'r')
    contents = file.read()
    file.close()
    return contents

if __name__ == '__main__':
    filename = sys.argv[1]
    time = reading_time(contents(filename))
    print('{} min read'.format(time))
