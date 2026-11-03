
from . import BaseFile, BaseData
import matplotlib.pyplot as plt
import os


def fnPlotTrainLine_WithField(inData, inFields, inYname, inTitleName, inDstDir):
    dfData = BaseData.fnGetDataFrame(inData)
    BaseFile.fnCreateDir(inDstDir)

    plt.figure()
    for inField in inFields:
        plt.plot(dfData[inField])

    # plt.ylim(-0.05, 1.05)
    plt.title(inTitleName)
    plt.ylabel(inYname)
    plt.xlabel('Epoch')
    plt.legend(inFields, loc='upper left')
    plt.savefig(os.path.join(inDstDir, 'train_{}.png'.format(inTitleName)))


def fnPlotTrainLine(inData, inFieldAccs, inFieldLosses, inDstDir):
    dfData = BaseData.fnGetDataFrame(inData)
    BaseFile.fnCreateDir(inDstDir)

    plt.figure()
    for inFieldAcc in inFieldAccs:
        plt.plot(dfData[inFieldAcc])

    # plt.ylim(-0.05, 1.05)
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(inFieldAccs, loc='upper left')
    plt.savefig(os.path.join(inDstDir, 'Accuracy_Epoch.png'))

    plt.figure()
    for inFieldLoss in inFieldLosses:
        plt.plot(dfData[inFieldLoss])
    # plt.ylim(-0.05, 1.55)
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(inFieldLosses, loc='upper left')
    plt.savefig(os.path.join(inDstDir, 'Loss_Epoch.png'))

def fnPlotTrainLine_NotSave(inData, inFieldTrainAcc, inFieldTrainLoss, inFieldTestAcc, inFieldTestLoss):
    dfData = BaseData.fnGetDataFrame(inData)

    plt.figure()
    plt.plot(dfData[inFieldTrainAcc])
    plt.plot(dfData[inFieldTestAcc])
    # plt.ylim(-0.05, 1.05)
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')


    plt.figure()
    plt.plot(dfData[inFieldTrainLoss])
    plt.plot(dfData[inFieldTestLoss])
    # plt.ylim(-0.05, 1.55)
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.show()
