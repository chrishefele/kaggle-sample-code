import pexpect
import sys
import time

SIM_EXE = 'mono /home/chefele/kaggle/FlightQuest2/download/exe/RunSimulation.exe'
SIM_PROMPT = 'Enter routes file name'

class Simulator:
    def __init__(self):
        self.sim = pexpect.spawn(SIM_EXE) # about 35 sec to initialize
        self.sim.expect(SIM_PROMPT, timeout=60) 

    def cost(self, sub_file):
        self.sim.sendline(sub_file)
        self.sim.expect(SIM_PROMPT, timeout=60)
        sim_output = self.sim.before # output between the last 2 expects
        assert 'Final Score' in sim_output
        for line in sim_output.split('\n'):
            if 'Final Score' in line:
                cost = float(line.split('$')[1]) # e.g. "Final Score: $12118.37"
                break
        return cost

    def stop(self):
        self.sim.sendline('')
        self.sim.close()
        del self.sim


if __name__=='__main__':
    print 'initializing simulator...'
    s = Simulator()
    print 'initialization complete'

    print s.cost('oneDaySampleSubmission10000.csv')
    print s.cost('oneDaySampleSubmission.csv')
    print s.cost('oneDaySampleSubmission10000.csv')
    s.stop()

"""
chefele@quatro:~$ mono /home/chefele/kaggle/FlightQuest2/download/exe/RunSimulation.exe
@11 ms: Loading configuration, projection, airports
@183 ms: Loading date-specific info 
- loaded weather
- loaded flights
- loaded airports
@34957 ms: Done with pre-simulation loads
-----------------------------------------------
Enter routes file name from /home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/
oneDaySampleSubmission10000.csv
Simulating 20130704_1540...
1024 of 1026 arrived - mean cost $12118.37, 2 messages
Messages:
* Flight 301823535 at (1112.4, 1157.6, 22791) cannot land at airport KBOS (1112.3, 1158.2, 20)
* Flight 301785086 at (-103.7, 476.5, 28551) cannot land at airport KDFW (-103.7, 476.5, 607)
Final Score: $12118.37 

Enter routes file name from /home/chefele/kaggle/FlightQuest2/download/OneDaySimulatorFiles/

chefele@quatro:~$ 
"""
