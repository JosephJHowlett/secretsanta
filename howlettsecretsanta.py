import numpy as np
import sys, os
import time
import matplotlib.pyplot as plt
from random import shuffle
import yaml


with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

entrant_data = config['entrants']

name_list = list(entrant_data)
name_list_orig = [name for name in name_list]

def rotate_list(l, n):
    return l[n:] + l[:n]

# TODO capitalize function

send_emails = True
print_assignments = True
# For test run - email all to Joey
test_run = True
plot = False

n_trials = 1
if plot:
    n_trials = 10000
outcomes = np.zeros((len(name_list_orig), n_trials), dtype=int)
for k in range(n_trials):
    # shuffle the list
    shuffle(name_list)

    name_map = {}
    index_map = {}
    for i in range(len(name_list)):
        name_map[i] = name_list[i]
        index_map[name_map[i]] = i

    start_over = True
    while start_over:
        left_to_pick = list(range(len(name_list)))
        assignments = []
        start_over = False
        for assign_ind in range(len(name_list)):
            options_to_pick = [i for i in left_to_pick]
            # dont let people pick themself
            if assign_ind in options_to_pick:
                options_to_pick.pop(np.where(np.asarray(options_to_pick)==assign_ind)[0][0])
            # remove avoidances from available assignments
            # if the persons name is in the avoidance map keys
            if 'avoid' in entrant_data[name_map[assign_ind]]:
                # get the indices of their avoidances
                avoid = entrant_data[name_map[assign_ind]]['avoid']
                if isinstance(avoid, (list, tuple)):
                    avoidance_indices = [
                        index_map[avoidance] for avoidance in avoid
                    ]
                else:
                    avoidance_indices = [index_map[avoid]]
                # remove their avoidances from their options if available
                for avoidance_index in avoidance_indices:
                    if avoidance_index in options_to_pick:
                        options_to_pick.pop(np.where(np.asarray(options_to_pick)==avoidance_index)[0][0])
            try:
                assignment = np.random.choice(np.asarray(options_to_pick, dtype=int))
                left_to_pick.pop(np.where(np.asarray(left_to_pick==assignment))[0][0])
                assignments.append(assignment)
            except ValueError:
                start_over = True
    for assign_ind in range(len(name_list)):
            orig_ind = name_list_orig.index(name_map[assign_ind])
            assigned_ind = name_list_orig.index(name_map[assignments[assign_ind]])
            outcomes[orig_ind, k] = assigned_ind

if plot:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    for assign_ind in range(len(name_list_orig)):
        plt.hist(outcomes[assign_ind], bins=len(name_list_orig), range=[-0.5, len(name_list_orig)-0.5], histtype='step', label=name_list_orig[assign_ind], weights=[assign_ind+1]*n_trials)
    plt.xticks(range(len(name_list_orig)), name_list_orig)
    plt.legend(loc=4)
    plt.show()

if print_assignments:
    for assign_ind in range(len(name_list)):
            print('%s, you are %s\'s secret santa!' % (
                name_map[assign_ind].upper(),
                name_map[assignments[assign_ind]].upper())
                )
            print(entrant_data[name_map[assign_ind]]['email'])
            print()

if send_emails:
    import smtplib
    from email.mime.text import MIMEText
    for i, assignment in enumerate(assignments):
        daemon = 'howlett.secret.santa.backup@gmail.com'
        if test_run:
            recipient = config['test_recipient_email']
        else:
            sys.exit()
            recipient = entrant_data[name_map[i]]['email']
        msg = MIMEText('Dear %s,\n\nYou are %s\'s Secret Santa!\n\nLove,\nRobots' % (name_map[i].upper(), name_map[assignment].upper()))
        msg['Subject'] = 'Your Secret Santa Assignment!!!!'
        #msg = MIMEText('Dear %s,\n\nI see you when you\'re sleeping!!!\n\nLove,\nRobots' % (name_map[i]))
        #msg['Subject'] = 'Secret Santa Test!!!!'
        msg['From'] = daemon
        msg['To'] = recipient 
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(
            "howlett.secret.santa.backup",
            os.environ['SECRETSANTAEMAILPASS']
        )
        server.sendmail(daemon, recipient, msg.as_string())
        server.quit()
        time.sleep(1)
