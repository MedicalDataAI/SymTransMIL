
# BaseData
import os
import pandas as pd
import copy
import numpy as np
import random as rn
from sklearn.model_selection import train_test_split

np.random.seed(101)
rn.seed(101)


def fnReadCsv(in_df_or_csv, inEncoding='utf-8'):
    res_df = None
    if isinstance(in_df_or_csv, str):
        if os.path.exists(in_df_or_csv):
            res_df = pd.read_csv(in_df_or_csv, encoding=inEncoding)
    elif isinstance(in_df_or_csv, pd.DataFrame):
        res_df = in_df_or_csv
    else:
        pass
    return res_df

def fnReadData(in_df_or_file, in_sheet_name=None, inEncoding='utf-8'):
    res_df = None
    if isinstance(in_df_or_file, str):
        if os.path.exists(in_df_or_file):
            if in_df_or_file.endswith(".csv"):
                res_df = pd.read_csv(in_df_or_file, encoding=inEncoding)
            elif in_df_or_file.endswith(".xls") or in_df_or_file.endswith(".xlsx"):
                if in_sheet_name is None:
                    res_df = pd.read_excel(in_df_or_file)
                else:
                    res_df = pd.read_excel(in_df_or_file, sheet_name=in_sheet_name)
    elif isinstance(in_df_or_file, pd.DataFrame):
        res_df = in_df_or_file
    else:
        pass
    return res_df

def fnGetDataFrame(inFpOrDf, in_sheet_name=None, inEncoding='utf-8'):
    res_df = fnReadData(inFpOrDf, in_sheet_name, inEncoding)
    return res_df

def fnGetDataFrame_SelFlag(inFpOrDf, inFieldFlag=None, in_sheet_name=None, inEncoding='utf-8'):
    dfRaw = fnGetDataFrame(inFpOrDf)
    if inFieldFlag is not None:
        dfRaw = fnSetDataFrameFieldType_Single(dfRaw, inFieldFlag, bool)
        dfData = dfRaw[dfRaw[inFieldFlag] == True]
        dfData = fnRestDataFrameIndex(dfData)
    else:
        dfData = dfRaw
    return dfData

# process
def fnSetDataFrameFieldType_Single(inData, inFieldName, inSetType):
    # set_dict_config = dict()
    # set_dict_config[idName] = str
    # set_dict_config[labelName] = int
    # set_dict_config[indexName] = int
    # dfData = dfData.astype(set_dict_config)
    if isinstance(inData[[inFieldName]], inSetType):
        pass
    else:
        inData[[inFieldName]] = inData[[inFieldName]].astype(inSetType)
    return inData

def fnSetDataFrameFieldType(inData, inFieldNames, inSetType):
    # set_dict_config = dict()
    # set_dict_config[idName] = str
    # set_dict_config[labelName] = int
    # set_dict_config[indexName] = int
    # dfData = dfData.astype(set_dict_config)
    set_dict_config = dict()
    for inFieldName in inFieldNames:
        set_dict_config[inFieldName] = inSetType
    dfData = inData.astype(set_dict_config)
    return dfData

def fnSetDataFrameFieldsType(inData, inFieldNames, inSetType):
    # set_dict_config = dict()
    # set_dict_config[idName] = str
    # set_dict_config[labelName] = int
    # set_dict_config[indexName] = int
    # dfData = dfData.astype(set_dict_config)
    set_dict_config = dict()
    for inFieldName in inFieldNames:
        set_dict_config[inFieldName] = inSetType
    dfData = inData.astype(set_dict_config)
    return dfData

def fnSetDataFrameFieldType(inData, inSetType):
    # set_dict_config = dict()
    # set_dict_config[idName] = str
    # set_dict_config[labelName] = int
    # set_dict_config[indexName] = int
    # dfData = dfData.astype(set_dict_config)
    inFieldNames = inData.columns.tolist()
    set_dict_config = dict()
    for inFieldName in inFieldNames:
        set_dict_config[inFieldName] = inSetType
    dfData = inData.astype(set_dict_config)
    return dfData

def fnSetDataFrameAllFieldType(inData, inSetType):
    # set_dict_config = dict()
    # set_dict_config[idName] = str
    # set_dict_config[labelName] = int
    # set_dict_config[indexName] = int
    # dfData = dfData.astype(set_dict_config)
    inFieldNames = inData.columns.tolist()
    set_dict_config = dict()
    for inFieldName in inFieldNames:
        set_dict_config[inFieldName] = inSetType
    dfData = inData.astype(set_dict_config)
    return dfData


def fnDataFrameAppend(inDf1, inDf2, inSetIgnoreIndex=True):
    dfRes = inDf1
    if inDf1 is None:
        dfRes = inDf2
    else:
        dfRes = dfRes.append(inDf2, ignore_index=inSetIgnoreIndex)
    return dfRes

def fnCombindDataFrame(inData1, inData2, inFieldId="ID", inSetIgnoreIndex=True):
    if inData1 is None:
        dfData1 = inData1
    else:
        dfData1 = fnGetDataFrame(inData1)
        dfData1 = fnSetDataFrameFieldType_Single(dfData1, inFieldId, str)
    dfData2 = fnGetDataFrame(inData2)
    dfData2 = fnSetDataFrameFieldType_Single(dfData2, inFieldId, str)
    return fnDataFrameAppend(dfData1, dfData2, inSetIgnoreIndex)

def fnMergeForLeftDataFrame(inDataLeft, inDataRight, inUidNames, inIsSort=False):
    dfLeft = fnGetDataFrame(inDataLeft)
    dfRight = fnGetDataFrame(inDataRight)

    dfLeft = fnSetDataFrameFieldsType(dfLeft, inUidNames, str)
    dfRight = fnSetDataFrameFieldsType(dfRight, inUidNames, str)
    dfRes = pd.merge(
        left=dfLeft, right=dfRight,
        on=inUidNames,
        how="left", left_on=None,
        right_on=None, left_index=False, right_index=False, sort=inIsSort)
    # dfRes = fnRestDataFrameIndex(dfRes)
    print("From Left_%d and Right_%d into %d ? %d." % (dfLeft.shape[0], dfRight.shape[0], dfRes.shape[0], dfLeft.shape[0]))
    return dfRes

def fnMergeForOuterDataFrame(inDataLeft, inDataRight, inUidNames, inIsSort=False):
    dfLeft = fnGetDataFrame(inDataLeft)
    dfRight = fnGetDataFrame(inDataRight)
    dfLeft = fnSetDataFrameFieldsType(dfLeft, inUidNames, str)
    dfRight = fnSetDataFrameFieldsType(dfRight, inUidNames, str)
    dfRes = pd.merge(
        left=dfLeft, right=dfRight,
        on=inUidNames,
        how="outer",
        left_on=None, right_on=None,
        left_index=False, right_index=False,
        sort=inIsSort)
    # dfRes = fnRestDataFrameIndex(dfRes)
    print("From Left_%d and Right_%d into %d ? %d." % (dfLeft.shape[0], dfRight.shape[0], dfRes.shape[0], dfLeft.shape[0]))
    return dfRes

# save
def fnSaveDataFrameIntoCsv(inData, inFp):
    resFlag = True
    try:
        if os.path.exists(inFp):
            os.remove(inFp)
        inData.to_csv(inFp, index=False, encoding='utf-8')
    except:
        resFlag = False
    return resFlag

def fnSaveDictIntoCsv(inData, inFp):
    save_df = pd.DataFrame(inData)
    fnSaveDataFrameIntoCsv(save_df, inFp)

def fnCopy(inData, isDeep=True):
    return copy.deepcopy(inData)

def fnGetRadomSplitIndex(inNum, inSplitTestRate=0.2, inSeed=101):
    # np.random.seed(inSeed)
    # shuffled_indices = np.random.permutation(inNum)
    # # test_ratio为测试集所占的半分比
    # test_set_size = int(inNum) * inSplitTestRate
    # indexTest = shuffled_indices[:(test_set_size-1)]
    # indexTrain = shuffled_indices[test_set_size:]
    indexAll = np.array(range(inNum))
    indexTrain, indexTest = train_test_split(indexAll, test_size=inSplitTestRate, shuffle=True, random_state=inSeed)
    return indexTrain, indexTest

def fnGetStratRadomSplitIndex(inLabelList, inSplitTestRate=0.2, inSeed=101):
    indexAll = np.array(range(len(inLabelList)))
    indexTrain, indexTest, _, _ = train_test_split(indexAll, inLabelList, test_size=inSplitTestRate, stratify=inLabelList, random_state=inSeed)
    return indexTrain, indexTest

def fnRestDataFrameIndex(inData):
    return inData.reset_index(drop=True)

def fnResetDataFrameIndex(inData):
    return inData.reset_index(drop=True)

def fnDropNaRowOfDf(inData):
    dfData = fnGetDataFrame(inData)
    return dfData.dropna(axis=0, how='any')

def fnShowFieldDistributeCnt(inDf, inFieldName):
    dfData = fnGetDataFrame(inDf)
    return dfData[inFieldName].value_counts()

def fnCheckStringMatch(inStr, inRefStr, inMode="equal"):
    flag = False
    if inMode == "equal":
        if inStr == inRefStr:
            flag = True
    elif inMode == "start":
        if inStr.startswith(inRefStr):
            flag = True
    elif inMode == "end":
        if inStr.endswith(inRefStr):
            flag = True
    else:
        flag = False
    return flag

def fnCheckStringMatchSelf(inStr, inRefStr, inMode="start"):
    tmpStr = inStr[0:len(inRefStr)]
    flag = False
    if inMode == "equal":
        if tmpStr == inRefStr:
            flag = True
    elif inMode == "start":
        if tmpStr.startswith(inRefStr):
            flag = True
    elif inMode == "end":
        if tmpStr.endswith(inRefStr):
            flag = True
    else:
        flag = False
    return flag

def fnPrintCountValues_Dict(inDict, inSetKey="Flag"):
    dfData = pd.DataFrame(inDict)
    res = fnShowFieldDistributeCnt(dfData, inSetKey)
    print("CountValues: ", res)
