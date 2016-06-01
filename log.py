import time

directory = './log/'

filename = time.strftime("%Y-%m-%d_%H")
file = open(directory + filename + '.txt', mode='a', encoding='utf-8')


def log(e):
    global filename, file

    log_text = ''
    if e.type == 'pubmsg':
        log_text = e.source.nick + ': ' + e.arguments[0]
    elif e.type == 'join':
        log_text = ' -- ' + e.source + ' has joined'
    elif e.type == 'quit':
        log_text = ' -- ' + e.source.nick + ' has quit (' + e.arguments[0] + ')'
    elif e.type == 'part':
        log_text = ' -- ' + e.source.nick + ' has left' + (' (' + e.arguments[0] + ')' if e.arguments else '')
    elif e.type == 'nick':
        log_text = ' -- ' + e.source.nick + ' has changed his nickname to ' + e.target
    elif e.type == 'kick':
        log_text = ' -- ' + e.source.nick + ' has kicked ' + e.arguments[0] + ' (' + e.arguments[1] + ')'
    elif e.type == 'mode':
        log_text = ' -- ' + e.source.nick + ' has set mode ' + ' '.join(e.arguments)

    filename_new = time.strftime("%Y-%m-%d_%H")
    if filename_new != filename:
        file.close()
        filename = filename_new
        file = open(directory + filename + '.txt', mode='a', encoding='utf-8')
    file.write(time.strftime("%M:%S") + ' ' + log_text + '\n')
    file.flush()
