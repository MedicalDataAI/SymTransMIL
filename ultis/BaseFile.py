# BaseFile
# from . import BaseFileEngine
# from . import BaseFloder
# from . import BaseFileClean
# from . import BaseSingleFile
from . import BaseData
import os
import glob
import shutil, time


### engine
# have bugs in no extend file
def fnCheckIsDir(inFp):
    return os.path.isdir(inFp)


def fnCheckIsExists(inFp):
    return os.path.exists(inFp)


def fnGetFuzzyFps(inFuzzyFp):
    return glob.glob(inFuzzyFp)


def fnGetFp(inDir, inFileName, inFileType="csv"):
    refStr = ".%s" % inFileType
    if inFileName.endswith(refStr):
        return os.path.join(inDir, inFileName)
    else:
        return os.path.join(inDir, "%s.%s" % (inFileName, inFileType))


def fnGetCsvFp(inDir, inFileName):
    return fnGetFp(inDir, inFileName, inFileType="csv")


def fnGetXmlFp(inDir, inFileName):
    return fnGetFp(inDir, inFileName, inFileType="xml")


### floder

def fnGetSubsInDir(path):
    rootdir = os.path.abspath(path)
    if not os.path.isdir(rootdir):
        my_msg = "%s is not folder." % rootdir
        print(my_msg)
        return None, None, None
    root_dir = []
    sub_dirs = []
    files = []
    for t_root_dir, t_sub_dirs, t_files in os.walk(rootdir):
        root_dir = t_root_dir
        sub_dirs = t_sub_dirs
        files = t_files
        break
    return root_dir, sub_dirs, files


def fnGetSubFileNum(inFp):
    root_dir, sub_dirs, files = fnGetSubsInDir(inFp)
    return len(sub_dirs)


def fnCreateDir(inFp):
    resFlag = True
    # if BaseFileEngine.fnCheckIsDir(inFp):
    #     if os.path.exists(inFp):
    #         os.makedirs(inFp)
    #         resFlag = True
    if os.path.exists(inFp):
        pass
    else:
        os.makedirs(inFp)
    return resFlag

# 创建新的文件夹
def fnCreateNewDir(inFp):
    resFlag = True
    # if BaseFileEngine.fnCheckIsDir(inFp):
    #     try:
    #         if os.path.exists(inFp):
    #             shutil.rmtree(inFp)
    #         os.makedirs(inFp)
    #     except:
    #         resFlag = False
    try:
        if os.path.exists(inFp):
            shutil.rmtree(inFp)
        os.makedirs(inFp)
    except:
        resFlag = False
    return resFlag

def fnCreateDirOfFile(inFp):
    if os.path.exists(inFp):
        pass
    else:
        fnCreateDir(os.path.dirname(inFp))
    pass

def fnDelFile(inFp):
    resFlag = True
    if fnCheckIsExists(inFp):
        try:
            os.remove(inFp)
        except:
            resFlag = False
    return resFlag

def fnDelFiles(inFps):
    resFlag = True
    for inFp in inFps:
        if not fnDelFile(inFp):
            resFlag = False
    return resFlag



# 删除文件夹
def fnDelDir(inFp):
    resFlag = True
    if fnCheckIsExists(inFp):
        try:
            shutil.rmtree(inFp)
        except:
            resFlag = False
    return resFlag

def fnDelFilePath(inFp):
    if os.path.exists(inFp):
        if fnCheckIsDir(inFp):
            return fnDelDir(inFp)
        else:
            return fnDelFile(inFp)
    else:
        return True
# 文件夹复制，从指定文件夹路径到新的路径
def fnCopyFloder(inSrcFp, inDstFp):
    # flagCreate = fnCreateNewDir(inDstFp)
    flagCreate = fnDelDir(inDstFp)
    if flagCreate:
        shutil.copytree(inSrcFp, inDstFp)
        return True
    else:
        return False

def fnCopyFile(inSrcFp, inDstFp):
    shutil.copyfile(inSrcFp, inDstFp)

def fnCopyFileIntoDir_WithFileDir(inSrcFp, inDstDir):
    dirName = os.path.basename(os.path.dirname(inSrcFp))
    dstDir = os.path.join(inDstDir, dirName)
    fnCreateNewDir(dstDir)
    fnCopyFpIntoRootDir(inSrcFp, dstDir)

def fnCopyFpIntoOtherFp(inSrcFp, inDstFp):
    if inSrcFp == inDstFp:
        return False
    if os.path.exists(inDstFp):
        return False
    fnCreateDir(os.path.dirname(inDstFp))
    if os.path.isdir(inSrcFp):
        shutil.copytree(inSrcFp, inDstFp)
    else:
        shutil.copyfile(inSrcFp, inDstFp)
    return True

def fnCopyFpIntoOtherFp_WithDel(inSrcFp, inDstFp):
    if inSrcFp == inDstFp:
        return False
    if os.path.exists(inDstFp):
        return fnDelFilePath(inDstFp)
    fnCreateDir(os.path.dirname(inDstFp))
    if os.path.isdir(inSrcFp):
        shutil.copytree(inSrcFp, inDstFp)
    else:
        shutil.copyfile(inSrcFp, inDstFp)
    return True

def fnCopyFpIntoRootDir(inSrcFp, inDstDir):
    dstFp = os.path.join(inDstDir, os.path.basename(inSrcFp))
    if os.path.exists(dstFp):
        return False

    fnCreateDir(inDstDir)
    if os.path.isdir(inSrcFp):
        shutil.copytree(inSrcFp, dstFp)
    else:
        shutil.copyfile(inSrcFp, dstFp)
    return True

# def fnCopyFpsIntoRootDir(inSrcFps, inDstDir):
#     listIndex = []
#     listInFp  = []
#     listFlag  = []
#     for index, inSrcFp in enumerate(inSrcFps):
#         dstFp = os.path.join(inDstDir, os.path.basename(inSrcFp))
#         if os.path.exists(dstFp):
#             return False
#
#     if os.path.exists(dstFp):
#         return False
#     if os.path.isdir(inSrcFp):
#         shutil.copytree(inSrcFp, dstFp)
#     else:
#         shutil.copyfile(inSrcFp, dstFp)
#     return True

def fnCopyFpsIntoRootDir(inSrcFps, inDstDir):
    listIndex = []
    listInFp = []
    listFlag = []
    fnCreateDir(inDstDir)
    for index, inSrcFp in enumerate(inSrcFps):
        print(r"[%d / %d] in %s." % (index+1, len(inSrcFps), os.path.basename(inSrcFp)))
        fnCopyFpIntoRootDir(inSrcFp, inDstDir)

    # if os.path.exists(dstFp):
    #     return False
    # if os.path.isdir(inSrcFp):
    #     shutil.copytree(inSrcFp, dstFp)
    # else:
    #     shutil.copyfile(inSrcFp, dstFp)
    return True

def fnBatchCopyFileIntoDir(inSrcDir, inDstDir, inFileType="NormalImage"):
    if inSrcDir == inDstDir:
        return
    fnCreateDir(inDstDir)
    _, _, fileNames = fnGetSubsInDir(inSrcDir)
    for index, fileName in enumerate(fileNames):
        inFp = os.path.join(inSrcDir, fileName)
        inFlag = False
        if "NormalImage".lower() == inFileType.lower():
            inFlag = fnCheckNormalImage(inFp)
        elif "None".lower() == inFileType.lower():
            inFlag = True
        else:
            if fileName.endswith(inFileType):
                inFlag = True
        myMsg = r"[%d / %d] in %s is %s." % (index+1, len(fileNames), fileName, inFlag)
        print(myMsg)
        if inFlag:
            fnCopyFpIntoRootDir(inFp, inDstDir)


# 复制文件夹到另外的根目录中
def fnCopyFloderIntoOtherRootDir(inSrcFp, inDstRootDir):
    dstFp = os.path.join(inDstRootDir, os.path.basename(inSrcFp))
    return fnCopyFloder(inSrcFp, dstFp)


def fnCopyFloderIntoOtherRootDir_FromDf(inSrcDir, inDstRootDir, inCsvFp, inFieldData, inFlag=None, inFlagType=bool, inSetFlagValue=False, inIsDir=True):
    fnCreateDir(inDstRootDir)
    dfRaw = BaseData.fnGetDataFrame(inCsvFp)
    dfDataRaw = BaseData.fnSetDataFrameFieldType_Single(dfRaw, inFieldData, str)
    if inFlag is None:
        dfDel = dfDataRaw
        pass
    else:
        dfDataRaw = BaseData.fnSetDataFrameFieldType_Single(dfDataRaw, inFlag, inFlagType)
        dfData = dfDataRaw[inSetFlagValue == dfDataRaw[inFlag]]
        dfData = BaseData.fnRestDataFrameIndex(dfData)

        dfDel = dfDataRaw[inSetFlagValue == dfDataRaw[inFlag]]
    tmpRootDir = os.path.dirname(inDstRootDir)
    tmpFp = os.path.join(tmpRootDir, "Info_"+os.path.basename(inDstRootDir)+".csv")
    BaseData.fnSaveDataFrameIntoCsv(dfDel, tmpFp)
    print("Convert Data %d into %d." % (dfRaw.shape[0], dfData.shape[0]))
    fnCreateNewDir(inDstRootDir)
    for index, fileName in dfData[inFieldData].iteritems():
        print(r"[%d /%d] in %s." % (index+1, dfData.shape[0], fileName))
        srcFp = os.path.join(inSrcDir, fileName)
        dstFp = os.path.join(inDstRootDir, fileName)

        if os.path.exists(srcFp):
            if inIsDir:
                fnCopyFloder(srcFp, dstFp)
            else:
                fnCopyFile(srcFp, dstFp)


def fnCopyMultiFpIntoOtherDir_RenameRepeatFp(inListFp, outDir, isDir=True):
    fnCreateDir(outDir)
    resDict = {
        "SrcDir": [],
        "SrcFileName": [],
        "SrcFp": [],
        "IsReapt": [],
        "Flag": [],
        "DstFileName": [],
        "DstFp": []
    }
    for indexDir, inDir in enumerate(inListFp):
        fpFuzzy = os.path.join(inDir, "*")
        inFps = glob.glob(fpFuzzy)
        for index, inFp in enumerate(inFps):
            fileName = os.path.basename(inFp)
            print(r"[%d / %d] in %s of %s [%d / %d]." % (
                index+1, len(inFps), fileName, os.path.basename(inDir), indexDir, len(inListFp)))
            dstFp = os.path.join(outDir, fileName)
            flag = False
            isReapt = False
            if fnCheckIsExists(dstFp):
                dstFp = os.path.join(outDir, "Reapt_"+fileName)
                isReapt = True

            if isDir:
                if fnCheckIsDir(inFp):
                    fnCopyFpIntoOtherFp(inFp, dstFp)
                    flag = True
            else:
                if not fnCheckIsDir(inFp):
                    fnCopyFpIntoOtherFp(inFp, dstFp)
                    flag = True
            resDict["SrcDir"].append(inDir)
            resDict["SrcFileName"].append(fileName)
            resDict["SrcFp"].append(inFp)
            resDict["IsReapt"].append(isReapt)
            resDict["Flag"].append(flag)
            resDict["DstFileName"].append(os.path.basename(dstFp))
            resDict["DstFp"].append(dstFp)
        pass
    fpSave = os.path.join(os.path.dirname(outDir), "Info_"+os.path.basename(outDir)+".csv")
    BaseData.fnSaveDictIntoCsv(resDict, fpSave)
    print(fpSave)

### floder
# 根据源路径指定目录下的新路径
def fnGetNewFp(inSrcFp, inNewAddStr):
    return os.path.join(os.path.dirname(inSrcFp), inNewAddStr + os.path.basename(inSrcFp))

def fnSplitAbsFilePath(in_fp):
    (filedir, tempfilename) = os.path.split(in_fp)
    (filename, extension) = os.path.splitext(tempfilename)
    return filedir, filename, extension

def fnGetMaskFileExtension_ForRadiomics(inFpMask):
    # resExtend = None
    if inFpMask.endswith(".nii.gz"):
        resExtend = ".nii.gz"
    elif inFpMask.endswith(".nii.gz"):
        resExtend = ".nii"
    else:
        resExtend = None

    return resExtend


def fnGetImageFileExtension_ForRadiomics(inFpImg, inSetImageType):
    """

    :param inFpImg:
    :param inSetImageType: DicomSingle, Normal
    :return:
    """
    resExtend = None
    if inSetImageType.lower() == "DicomSingle".lower() or inSetImageType.lower() == "Normal".lower():
        if inSetImageType.lower() == "DicomSingle".lower() and inFpImg.endswith(".nii.gz"):
            resExtend = ".nii.gz"
        else:
            _, _, resExtend = fnSplitAbsFilePath(inFpImg)
    return resExtend


def fnGetIdFromFileOrDir(inFp):
    idRes = None
    if fnCheckIsDir(inFp):
        idRes = os.path.basename(inFp)
    else:
        if fnCheckNormalImage(inFp):
            _, idRes, _ = fnSplitAbsFilePath(inFp)
        elif inFp.endswith(".nii.gz"):
            fileName = os.path.basename(inFp)
            idRes = fileName[:-len(".nii.gz")]
        elif inFp.endswith(".nii"):
            fileName = os.path.basename(inFp)
            idRes = fileName[:-len(".nii")]
        else:  # DicomSingle or nii.gz
            pass
    return idRes


def fnCheckNormalImage(inFp, inImgType=[]):
    resFlag = False
    # imgName = os.path.basename(inFp)
    imgName = inFp.lower()
    if imgName.endswith(".bmp") or imgName.endswith(".jpg") or imgName.endswith(".png") or imgName.endswith(
            ".tif") or imgName.endswith(".jpeg") or imgName.endswith(".tiff"):
        resFlag = True
    if resFlag:
        return resFlag
    for imgType in inImgType:
        if imgName.endswith(imgType):
            resFlag = True
            break
    return resFlag

def fnCheckImageTypeIsDefine_ForRadiomics(inFp, inSetImageType):
    """

    :param inFp:
    :param inImageType: DicomSerial, DicomSingle, Normal
    :return:
    """

    if fnCheckIsDir(inFp):
        resImgType = "DicomSerial"
    else:
        if fnCheckNormalImage(inFp):
            resImgType = "Normal"
        else:
            fpLower = inFp.lower()
            if fpLower.endswith(".nii.gz") or fpLower.endswith(".nii") or fpLower.endswith(".dcm"):
                resImgType = "DicomSingle"
            else:
                resImgType = "None"
    return resImgType.lower() == inSetImageType.lower()

def fnCheckMaskFile(inFp, inFileTypes=[".nii", ".nii.gz", ".nrrd"]):
    resFlag = False
    imgName = inFp.lower()
    for fileType in inFileTypes:
        if imgName.endswith(fileType):
            resFlag = True
            break
    return resFlag


# None Normal Dicom NII  DicomSingle bmp jpeg ****
# 判断指定文件夹中是否只有一个文件
def fnCheckJustOneFileInDir(inDirFp, inFileTYpe="None"):
    resFlag = False
    resMsg = ""
    resFp = None
    _, _, fileNames = fnGetSubsInDir(inDirFp)
    if "None".lower() == inFileTYpe.lower():
        if 1 == len(fileNames):
            resFlag = True
            resMsg = "Success"
            resFp = os.path.join(inDirFp, fileNames[0])
        else:
            resMsg = "FileNumIs%d" % len(fileNames)
    elif "Normal".lower() == inFileTYpe.lower():
        fileCnt = 0
        for fileName in fileNames:
            if fnCheckNormalImage(fileName):
                fileCnt += 1
                resFp = os.path.join(inDirFp, fileName)
        if 1 == fileCnt:
            resFlag = True
            resMsg = "Success"
        else:
            resMsg = "FileNumIs%d" % fileCnt
            resFp = None
    elif "Dicom".lower() == inFileTYpe.lower():
        fileCnt = 0
        for fileName in fileNames:
            if ~fnCheckNormalImage(fileName):
                fileCnt += 1
                resFp = os.path.join(inDirFp, fileName)
        if 1 == fileCnt:
            resFlag = True
            resMsg = "Success"
        else:
            resMsg = "FileNumIs%d" % fileCnt
            resFp = None
    else:
        # .dcm .bmp .jpeg
        fileCnt = 0
        for fileName in fileNames:
            if fileName.lower().endswith("." + inFileTYpe.lower()):
                fileCnt += 1
                resFp = os.path.join(inDirFp, fileName)
        if 1 == fileCnt:
            resFlag = True
            resMsg = "Success"
        else:
            resMsg = "FileNumIs%d" % fileCnt
            resFp = None
        pass

    return resFlag, resMsg, resFp

# rename
# 按照指定fuzzy所有文件名替换指定字符
def fnReplanceChr(inFuzzy, inOldChr=" ", inNewChr="_", isDir=True, outFileName=None):
    inFps = glob.glob(inFuzzy)
    cnt = 0

    resDict = {
        "Name": [],
        "Flag": [],
        "NewName": []
    }
    for inFp in inFps:
        cnt += 1
        fpDir = os.path.dirname(inFp)
        fpName = os.path.basename(inFp)

        setFlag = False
        setName = fpName
        setNewName = None
        if isDir:
            if os.path.isdir(inFp) and (inOldChr in fpName):
                newFpName = fpName.replace(inOldChr, inNewChr)
                dstFp = os.path.join(fpDir, newFpName)
                os.rename(inFp, dstFp)

                setFlag = True
                setNewName = newFpName
            else:
                myMsg = "[%d / %d] in %s is dir_%s and %s_%s." % (
                    cnt, len(inFps), fpName, os.path.isdir(inFp), inOldChr, (inOldChr in fpName))
                print(myMsg)
        else:
            if os.path.isfile(inFp) and (inOldChr in fpName):
                newFpName = fpName.replace(inOldChr, inNewChr)
                dstFp = os.path.join(fpDir, newFpName)
                os.rename(inFp, dstFp)

                setFlag = True
                setNewName = newFpName
            else:
                myMsg = "[%d / %d] in %s is dir_%s and %s_%s." % (
                    cnt, len(inFps), fpName, os.path.isdir(inFp), inOldChr, (inOldChr in fpName))
                print(myMsg)
        resDict["Name"].append(setName)
        resDict["Flag"].append(setFlag)
        resDict["NewName"].append(setNewName)
    fpSave = None
    if cnt > 0:
        fpDir = os.path.dirname(inFps[0])
        if outFileName is None:
            fpSave = os.path.join(os.path.dirname(fpDir), "InfoRename_"+os.path.basename(fpDir)+".csv")
        else:
            fpSave = os.path.join(os.path.dirname(fpDir), outFileName)
        BaseData.fnSaveDictIntoCsv(resDict, fpSave)
        print(fpSave)
    return fpSave

def fnReplaceFilePaths(inFps, inOldChr=" ", inNewChr="_", isDir=True, inDstDir = None):
    cnt = 0
    resDict = {
        "Name": [],
        "Flag": [],
        "NewName": []
    }
    for index, inFp in enumerate(inFps):
        print(r"[%d / %d] in %s." % (index+1, len(inFps), os.path.basename(inFp)))
        cnt += 1
        fpDir = os.path.dirname(inFp)
        fpName = os.path.basename(inFp)

        setFlag = False
        setName = fpName
        setNewName = None
        if isDir:
            if os.path.isdir(inFp) and (inOldChr in fpName):
                newFpName = fpName.replace(inOldChr, inNewChr)
                dstFp = os.path.join(fpDir, newFpName)
                if inDstDir is None:
                    os.rename(inFp, dstFp)
                else:
                    dstFp = os.path.join(inDstDir, newFpName)
                    fnCopyFpIntoOtherFp_WithDel(inFp, dstFp)
                setFlag = True
                setNewName = newFpName
            else:
                myMsg = "[%d / %d] in %s is dir_%s and %s_%s." % (
                    cnt, len(inFps), fpName, os.path.isdir(inFp), inOldChr, (inOldChr in fpName))
                print(myMsg)
        else:
            if os.path.isfile(inFp) and (inOldChr in fpName):
                newFpName = fpName.replace(inOldChr, inNewChr)
                dstFp = os.path.join(fpDir, newFpName)
                # os.rename(inFp, dstFp)
                if inDstDir is None:
                    os.rename(inFp, dstFp)
                else:
                    dstFp = os.path.join(inDstDir, newFpName)
                    fnCopyFpIntoOtherFp_WithDel(inFp, dstFp)
                setFlag = True
                setNewName = newFpName
            else:
                myMsg = "[%d / %d] in %s is dir_%s and %s_%s." % (
                    cnt, len(inFps), fpName, os.path.isdir(inFp), inOldChr, (inOldChr in fpName))
                print(myMsg)
        resDict["Name"].append(setName)
        resDict["Flag"].append(setFlag)
        resDict["NewName"].append(setNewName)
    return resDict

def fnReplaceFilePath_ByFuzzy(inFuzzyFp, inOldChr=" ", inNewChr="_", isDir=True, inDstDir = None):
    inFps = glob.glob(inFuzzyFp)
    return fnReplaceFilePaths(inFps=inFps, inOldChr=inOldChr, inNewChr=inNewChr, isDir=isDir, inDstDir=inDstDir)

def fnRenameAdd(inFuzzy, inAddStr="id_", isDir=True):
    inFps = glob.glob(inFuzzy)
    for index, inFp in enumerate(inFps):
        fileName = os.path.basename(inFp)
        print(r"[%d/ %d] in %s." % (index+1, len(inFps), fileName))
        if fileName.startswith(inAddStr):
            continue

        newFp = fnGetNewFp(inFp, inAddStr)
        if isDir:
            if fnCheckIsDir(inFp):
                os.rename(inFp, newFp)
        else:
            if not fnCheckIsDir(inFp):
                os.rename(inFp, newFp)
            pass
    pass

def fnConvertCategoryDirIntoCsvLabel(inDirFuzzy):
    inFps = glob.glob(inDirFuzzy)
    resDict = {
        "Index": [],
        "Label": [],
        "FileName": [],
        "FP": []
    }
    print(len(inFps))
    if len(inFps) > 10:
        fpDir = os.path.dirname(inFps[0])
        cnt = 0
        for inFp in inFps:
            fpDir = os.path.dirname(inFp)
            resDict["Index"].append(cnt)
            resDict["Label"].append(os.path.basename(fpDir))
            resDict["FileName"].append(os.path.basename(inFp))
            resDict["FP"].append(inFp)
            cnt += 1
        clfDir = os.path.dirname(fpDir)
        saveFp = os.path.join(clfDir, "info_label_" + os.path.basename(clfDir) + ".csv")
        BaseData.fnSaveDictIntoCsv(resDict, saveFp)
        print(saveFp)
        saveFp = os.path.join(clfDir, "info_label.csv")
        BaseData.fnSaveDictIntoCsv(resDict, saveFp)
    else:
        pass
    pass

def fnCopyCategoryDirIntoSingleDir(
        in_src_root_dir, in_clf_num=2, in_dst_dir=None, in_id_name='FileName',
        in_label_name='Label'):
    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    if in_dst_dir is None:
        dst_dir = os.path.join(os.path.dirname(in_src_root_dir), os.path.basename(in_src_root_dir) + '_' + time_str)
    else:
        dst_dir = in_dst_dir
    # make_new_dir(dst_dir)
    dst_data_dir = os.path.join(dst_dir, 'datasets')
    dst_data_csv = os.path.join(dst_dir, 'info.csv')
    dst_err_data_csv = os.path.join(dst_dir, 'err_datasets.csv')
    fnCreateNewDir(dst_data_dir)

    use_file_list = []
    use_label_list = []
    repeat_file_list = []

    for category_index in range(0, in_clf_num):
        src_category_dir = os.path.join(in_src_root_dir, str(category_index))
        src_fuzzy_name = os.path.join(src_category_dir, '*')
        src_fps = glob.glob(src_fuzzy_name)
        my_msg = "start convert %d images in category %d into %s." % (len(src_fps), category_index, dst_data_dir)
        print(my_msg)
        for tmp_src_fp in src_fps:
            if fnCopyFpIntoRootDir(tmp_src_fp, dst_data_dir):
                use_file_list.append(os.path.basename(tmp_src_fp))
                use_label_list.append(category_index)
            else:
                repeat_file_list.append(os.path.basename(tmp_src_fp))
                my_msg = "      find %d repeat file in %s." % (len(repeat_file_list), tmp_src_fp)
                print(my_msg)
    my_msg = "Find %d repeat images, and success convert %d images." % (len(repeat_file_list), len(use_file_list))
    print(my_msg)
    data_dict = dict()
    data_dict[in_id_name] = use_file_list
    data_dict[in_label_name] = use_label_list
    BaseData.fnSaveDictIntoCsv(data_dict, dst_data_csv)
    if len(repeat_file_list) > 0:
        err_data_dict = dict()
        err_data_dict[in_id_name] = repeat_file_list
        BaseData.fnSaveDictIntoCsv(err_data_dict, dst_err_data_csv)
        print(dst_err_data_csv)

def fnGetNormalImageType(inImgFp):
    tmpNames = inImgFp.split(sep=".")
    return tmpNames[-1]

def fnGetIdNamefFromFile(inFp, inImgType="NormalImage"):
    inFileName = os.path.basename(inFp)
    # idName = None
    if inImgType.lower() == "NormalImage".lower():
        imgType = fnGetNormalImageType(inFp)
        subLen = 1+len(imgType)
        idName = inFileName[:-subLen]
    elif inImgType.lower() == "None".lower():
        idName = inFileName
    else:
        idName = inFileName[:-(1+len(inImgType))]
    return idName

def fnMatchImageFileAndMaskFile(inImgDir, inMaskDir, inImgType="NormalImage", inMaskType="nii.gz", outFileName=None):
    # inImgType="NormalImage" / "Dir"
    outDir = os.path.dirname(inImgDir)
    if outFileName is None:
        outFileName = "Info_"+os.path.basename(inImgDir)+"_"+os.path.basename(inMaskDir)+".csv"
    fpSave = os.path.join(outDir, outFileName)
    # print(fpSave)
    resDict = {
        "Id": [],
        "Flag": [],
        "Msg": [],
        "ImageFileName": [],
        "MaskFileName": [],
        "ImageFp": [],
        "MaskFp": []
    }
    _, _, fileNames = fnGetSubsInDir(inImgDir)
    for index, fileName in enumerate(fileNames):
        setFlag = False
        if inImgType.lower() == "NormalImage".lower():
            setFlag = fnCheckNormalImage(fileName)
        elif inImgType.lower() == "None".lower():
            setFlag = True
        else:
            if fileName.endswith(inImgType):
                setFlag = True
        setMsg = "Success"
        setIdName = None

        setImgName = None
        setMaskName = None
        setfpImg = None
        setfpMask = None
        if setFlag:
            setImgName = fileName
            setIdName = fnGetIdNamefFromFile(setImgName, inImgType)
            setfpImg = os.path.join(inImgDir, setImgName)
            setMaskName = setIdName+"."+inMaskType
            setfpMask = os.path.join(inMaskDir, setMaskName)
            if fnCheckIsExists(setfpMask):
                pass
            else:
                setFlag = False
                setMsg = "Not Find Mask File."
                setMaskName = None
                setfpMask = None
        else:
            setMsg = "Not Image File."
        myMsg = r"[%d / %d] in %s is %s." % (index+1, len(fileNames), fileName, setFlag)
        print(myMsg)

        resDict["Id"].append(setIdName)
        resDict["Flag"].append(setFlag)
        resDict["Msg"].append(setMsg)
        resDict["ImageFileName"].append(setImgName)
        resDict["MaskFileName"].append(setMaskName)
        resDict["ImageFp"].append(setfpImg)
        resDict["MaskFp"].append(setfpMask)
    BaseData.fnSaveDictIntoCsv(resDict, fpSave)
    print(fpSave)

def fnCheckFileExistsForRadiomics(inFpCsv, inFieldFlag, inFieldId, inFieldNewId):
    dfData = BaseData.fnGetDataFrame(inFpCsv)
    dfData = BaseData.fnSetDataFrameFieldType_Single(dfData, inFieldFlag, bool)
    # setNewIdFlag = []
    if inFieldFlag is None:
        setNewIdFlag = []
        for index, rowData in dfData.iterrows():
            if fnCheckIsExists(rowData[inFieldId]):
                setNewIdFlag.append(True)
            else:
                setNewIdFlag.append(False)
        dfData[inFieldNewId] = setNewIdFlag
    else:
        setNewIdFlag = []
        for index, rowData in dfData.iterrows():
            if rowData[inFieldFlag]:
                if fnCheckIsExists(rowData[inFieldId]):
                    setNewIdFlag.append(True)
                else:
                    setNewIdFlag.append(False)
            else:
                setNewIdFlag.append(False)
        dfData[inFieldNewId] = setNewIdFlag
    return dfData

