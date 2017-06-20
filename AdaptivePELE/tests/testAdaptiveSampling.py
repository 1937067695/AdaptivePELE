import unittest
import pickle
import shutil
import os
import AdaptivePELE.adaptiveSampling as adaptiveSampling
import AdaptivePELE.atomset.atomset as atomset
from AdaptivePELE.clustering import clustering
import socket


class TestadaptiveSampling(unittest.TestCase):

    def checkClusteringObjects(self, goldenClusters, outputPath):
        # goldenPathObject = os.path.join(goldenPath, "%d/clustering/object.pkl")
        outputPathObject = os.path.join(outputPath, "%d/clustering/object.pkl")
        for i in range(2, 3):
            with open(outputPathObject % i, 'rb') as f2:
                outputCluster = pickle.load(f2)
            # with open(goldenPathObject % i, 'rb') as f:
            #     goldenCluster = pickle.load(f)
            # outputCluster.clusters.printClusters()
            self.assertEqual(outputCluster.clusters.getNumberClusters(), len(goldenClusters))
            for goldCl, outCl in zip(goldenClusters, outputCluster.clusters.clusters):
                self.assertEqual(outCl, goldCl)

    def checkStartingConformations(self, goldenPath, outputPath):
        goldenPathInitial = os.path.join(goldenPath, "%d/initial_%d.pdb")
        outputPathInitial = os.path.join(outputPath, "initial_%d_%d.pdb")

        j = 0
        for j in range(3):
            for ij in range(1, 5):
                goldenInitial = atomset.PDB()
                goldenInitial.initialise(goldenPathInitial % (j, ij))

                outputInitial = atomset.PDB()
                if j == 0:
                    # initial structures will always be "initial_0_0.pdb"
                    outputInitial.initialise(outputPathInitial % (j, 0))
                else:
                    outputInitial.initialise(outputPathInitial % (j, ij % 4))
                self.assertEqual(goldenInitial, outputInitial)

    def checkTrajectories(self, goldenPath, outputPath):
        goldenPathTrajectory = os.path.join(goldenPath, "%d/trajectory_%d.pdb")
        outputPathTrajectory = os.path.join(outputPath, "%d/trajectory_%d.pdb")

        for epoch in range(3):
            for i in range(1, 5):
                goldenTrajFile = open(goldenPathTrajectory % (epoch, i), 'r')
                goldenTraj = goldenTrajFile.read()

                goldenTrajFile.close()
                outputTrajFile = open(outputPathTrajectory % (epoch, i), 'r')
                outputTraj = outputTrajFile.read()
                outputTrajFile.close()
                self.assertEqual(goldenTraj, outputTraj)

    def integrationTest(self, controlFile, goldenPath, outputPath, goldenClusters):
        # Function to test --> integration test
        adaptiveSampling.main(controlFile)

        # Assertions
        tmpFolder = "tmp_" + outputPath.replace("/", "_")

        self.checkClusteringObjects(goldenClusters, outputPath)
        self.checkStartingConformations(goldenPath, tmpFolder)
        self.checkTrajectories(goldenPath, outputPath)

        # cleanup
        shutil.rmtree(outputPath)
        shutil.rmtree(tmpFolder)

    def testIntegration1(self):
        """
            Simulations are not run, trajectories and reports are copied
        """
        controlFile = "tests/data/3ptb_data/integrationTest1.conf"
        goldenPath = "tests/data/3ptb_data/originTest1"
        outputPath = "tests/data/3ptb_data/Test1"
        elements = [28, 17, 5, 18, 1, 3]
        goldenClusters = []
        for i in range(6):
            pdb = atomset.PDB()
            pdb.initialise(goldenPath+"/2/clustering/cluster_%d.pdb" % i, resname="AEN")
            cluster = clustering.Cluster(pdb, thresholdRadius=4)
            cluster.elements = elements[i]
            cluster.contacts = 0
            goldenClusters.append(cluster)
        self.integrationTest(controlFile, goldenPath, outputPath, goldenClusters)

    def testIntegration2(self):
        """
            Simulations are not run, trajectories and reports are copied
        """
        controlFile = "tests/data/3ptb_data/integrationTest2.conf"
        goldenPath = "tests/data/3ptb_data/srcTest2Epsilon"
        outputPath = "tests/data/3ptb_data/Test2"
        elements = [35, 14, 8, 14, 1]
        metrics = [[1.0, 0.0, 0.0, -7498.07, 20.1909, 0.216436],
                   [1.0, 0.0, 0.0, -7498.06, 18.5232, 0.229384],
                   [1.0, 0.0, 0.0, -7498.01, 18.6059, 0.253929],
                   [1.0, 0.0, 0.0, -7498.05, 22.4539, 0.238184],
                   [1.0, 4.0, 4.0, -7498.05, 22.7766, 0.242335]
                  ]
        goldenClusters = []
        for i in range(5):
            pdb = atomset.PDB()
            pdb.initialise(goldenPath+"/2/clustering/cluster_%d.pdb" % i, resname="AEN")
            cluster = clustering.Cluster(pdb, 4, metrics=metrics[i])
            cluster.elements = elements[i]
            cluster.contacts = 0
            goldenClusters.append(cluster)

        self.integrationTest(controlFile, goldenPath, outputPath, goldenClusters)

    def testIntegration3(self):
        """
            Simulations are actually run
        """
        controlFile = "tests/data/3ptb_data/integrationTest3.conf"
        goldenPath = "tests/data/3ptb_data/originTest3"
        outputPath = "tests/data/3ptb_data/Test3"
        elements = [27, 22, 21, 2]
        goldenClusters = []
        for i in range(4):
            pdb = atomset.PDB()
            pdb.initialise(goldenPath+"/2/clustering/cluster_%d.pdb" % i, resname="AEN")
            cluster = clustering.Cluster(pdb, 4)
            cluster.elements = elements[i]
            cluster.contacts = 0
            goldenClusters.append(cluster)
        name = socket.gethostname()
        if "bsccv" not in name and "login" not in name:
            print "Some integration can't be run due to not having PELE  installed"
            return True
        self.integrationTest(controlFile, goldenPath, outputPath, goldenClusters)

    def testRestartEmptyClustering(self):
        controlFile = "tests/data/3ptb_data/restartTest.conf"
        outputPath = "tests/data/3ptb_data/RestartTest"
        tmpFolder = "tmp_" + outputPath.replace("/", "_")
        clusteringObjectPath = os.path.join(outputPath, "2", "clustering", "object.pkl")
        if not os.path.exists(os.path.join(outputPath, "1", "clustering")):
            os.makedirs(os.path.join(outputPath, "1", "clustering"))
        name = socket.gethostname()
        if "bsccv" not in name and "login" not in name:
            print "Some integration can't be run due to not having PELE  installed"
            return True
        # Function to test --> integration test
        shutil.copy("tests/data/3ptb_data/object_test_bk.pkl", os.path.join(outputPath, "1", "clustering", "object.pkl"))
        adaptiveSampling.main(controlFile)
        # Assertions
        self.assertTrue(adaptiveSampling.checkIntegrityClusteringObject(clusteringObjectPath))
        # Remove clustering object from the simulation and create and empty one
        open(clusteringObjectPath, "w").close()
        # cleanup
        shutil.rmtree(tmpFolder)