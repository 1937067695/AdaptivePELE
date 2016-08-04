import time
import os
import constants
import subprocess
import blockNames
import shutil
import simulationTypes
import string

class SimulationParameters:
    def __init__(self):
        self.processors = 0
        self.executable = ""
        self.templetizedControlFile = ""
        self.dataFolder = ""
        self.documentsFolder = ""
        self.iterations = 0
        self.peleSteps = 0
        self.seed = 0

class SimulationRunner:
    def __init__(self, parameters):
        self.parameters = parameters
    
    def runSimulation(self, runningControlFile = ""):
        pass 

    def makeWorkingControlFile(self, templ, work, dictionary):
        pass

class PeleSimulation(SimulationRunner):
    def __init__(self, parameters):
        SimulationRunner.__init__(self, parameters)
        self.type = simulationTypes.SIMULATION_TYPE.PELE
    
    def makeWorkingControlFile(self, templetizedControlFile, workingControlFilename, dictionary):
        inputFile = open(templetizedControlFile, "r")
        inputFileContent = inputFile.read()
        inputFile.close()

        inputFileTemplate = string.Template(inputFileContent)
        outputFileContent = inputFileTemplate.substitute(dictionary)

        outputFile = open(workingControlFilename, "w")
        outputFile.write(outputFileContent)
        outputFile.close()

    def createSymbolicLinks(self):
        if not os.path.islink("Data"):
            os.system("ln -s " + self.parameters.dataFolder + " Data")
        if not os.path.islink("Documents"):
            os.system("ln -s " + self.parameters.documentsFolder + " Documents")


    def runSimulation(self, runningControlFile = ""):
        self.createSymbolicLinks()

        toRun = ["mpirun -np " + str(self.parameters.processors), self.parameters.executable, runningControlFile]
        toRun = " ".join(toRun)
        print toRun
        startTime = time.time() 
        proc = subprocess.Popen(toRun, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print out
        if err: print err

        endTime = time.time() 
        print "PELE took %.2f sec" % (endTime - startTime)

class TestSimulation(SimulationRunner):
    def __init__(self, parameters):
        self.type = simulationTypes.SIMULATION_TYPE.TEST
        self.copied = False
        self.parameters = parameters

    def runSimulation(self, runningControlFile = ""):
        if not self.copied:
            if os.path.exists(self.parameters.destination):
                shutil.rmtree(self.parameters.destination)
            shutil.copytree(self.parameters.origin, self.parameters.destination)
            self.copied = True

class RunnerBuilder:

    def build(self, simulationRunnerBlock):
        simulationType = simulationRunnerBlock[blockNames.SIMULATION_TYPE.type]
        paramsBlock = simulationRunnerBlock[blockNames.SIMULATION_PARAMS.params]
        params = SimulationParameters()
        if simulationType == blockNames.SIMULATION_TYPE.PELE:
            params.processors = paramsBlock[blockNames.SIMULATION_PARAMS.processors]
            params.dataFolder = paramsBlock.get(blockNames.SIMULATION_PARAMS.dataFolder, constants.DATA_FOLDER)
            params.documentsFolder = paramsBlock.get(blockNames.SIMULATION_PARAMS.documentsFolder, constants.DOCUMENTS_FOLDER)
            params.executable = paramsBlock.get(blockNames.SIMULATION_PARAMS.executable, constants.PELE_EXECUTABLE)
            params.templetizedControlFile = paramsBlock[blockNames.SIMULATION_PARAMS.templetizedControlFile]
            params.iterations = paramsBlock[blockNames.SIMULATION_PARAMS.iterations]
            params.peleSteps = paramsBlock[blockNames.SIMULATION_PARAMS.peleSteps]
            params.seed = paramsBlock[blockNames.SIMULATION_PARAMS.seed]

            SimulationRunner = PeleSimulation(params)
        elif simulationType == blockNames.SIMULATION_TYPE.MD:
            pass
        elif simulationType == blockNames.SIMULATION_TYPE.TEST:
            params.processors = paramsBlock[blockNames.SIMULATION_PARAMS.processors]
            params.destination = paramsBlock[blockNames.SIMULATION_PARAMS.destination]
            params.origin = paramsBlock[blockNames.SIMULATION_PARAMS.origin]
            params.iterations = paramsBlock[blockNames.SIMULATION_PARAMS.iterations]
            params.peleSteps = paramsBlock[blockNames.SIMULATION_PARAMS.peleSteps]
            params.seed = paramsBlock[blockNames.SIMULATION_PARAMS.seed]
            SimulationRunner = TestSimulation(params)
        else:
            sys.exit("Unknown simulation type! Choices are: " + str(simulationTypes.SIMULATION_TYPE_TO_STRING_DICTIONARY.values()))
        return SimulationRunner

