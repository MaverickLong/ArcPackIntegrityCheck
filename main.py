# Arcaea Songlist & Package Integrity Checker
# 
# Version: 1.5-CHS
# 
# Last Edited: September 2 2022
#
# Distributed Under the GPLv3 Lisence: https://www.gnu.org/licenses/gpl-3.0.en.html
#
# Modifications:
# Added check for existence of Silent Answer in packlist.
# Added check for hidden_until element.
# Corrected typos.
#
# To-dos:
# Increase readibility

from operator import truediv
from os import walk
from os.path import exists
import json
from re import match

version = "1.5-CHS"

fileList = ["base.jpg","base_256.jpg","base.ogg"]

eliminateNameList = ["random","pack","tutorial"]

songlistTextElementList = ["artist","bpm","version", "purchase","bg","set"]
songlistNumElementList = ["bpm_base"]

difficultiesTextElementList = ["chartDesigner", "jacketDesigner"]

ratingClassName = ["Past, Present, Future, Beyond"]

standalone = False
checkBgIntegrity = True

# Configs
allowBydAff = False
allowNotASCIIFileName = False
checkDiamondIntegrity = False
useAssetsDirWhileCheckAll = False
useBgDirInsteadOfImgDir = True
diamondList = {}

directory = ""
bgDirectory = ""

def checkSonglistInFolder():
    songList = resolveSonglist()
    dirs = scanSongDirectory()
    for song in songList:
        inSongFolder = False
        for songFolderName in dirs:
            if song['id'] in dirs or ("dl_" + song['id']) == songFolderName:
                inSongFolder = True
                break
        if not inSongFolder:
            print("id 为 " + song['id'] + " 的曲目在songlist中, 但不在文件夹中")

def checkFolderInSonglist():
    songList = resolveSonglist()
    dirs = scanSongDirectory()
    for songFolderName in dirs:
        inSongList = False
        for song in songList:
            if song['id'] == songFolderName or ("dl_" + song['id']) == songFolderName:
                inSongList = True
                break
        if not inSongList:
            if songFolderName != "pack" and songFolderName != "random":
                print("id 为 " + songFolderName + " 的曲目在文件夹中, 但不在songlist中")
                pass

def checkAssetIntegrity():
    dirs = scanSongDirectory()
    for songFolderName in dirs:
        for rootS, dirsS, filesS in walk(directory + "/" + songFolderName, topdown=False):
            if allowNotASCIIFileName:
                pass
            else:
                for file in filesS:
                    if match("^[ -~]*$", file) == None:
                        print("在文件夹 " + songFolderName + " 中有非ASCII文件名的文件: " + file)
        if songFolderName.startswith("dl_"):
            print("跳过下载文件夹 " + songFolderName)
            continue
        for checkObj in fileList:
            if checkObj not in filesS:
                print("在文件夹 " + songFolderName + " 中没有找到有效的" + checkObj + " 文件.")
        withAff = False
        for aff in filesS:
            if allowBydAff:
                if match("[0-3].aff", aff) != None:
                    withAff = True
            else:
                if match("[0-2].aff", aff) != None:
                    withAff = True
        if not withAff:
            print("在文件夹 " + songFolderName + " 中没有找到有效的谱面(.aff)文件.")

def checkSonglistElement():
    songList = resolveSonglist()
    if not standalone:
        packList = resolvePacklist()
    bgDir = inputBgDir()
    songIdList = []
    for song in songList:

        # Test for missing/duplicate Song ID
        if not "id" in song.keys():
            print("应有的项目 \"id\" 在一首曲目中未找到. 该曲目的信息如下所示:\n" + str(song))
            id = "SongID未找到"
        else:
            id = song["id"]
        if id in songIdList:
            print("发现使用重复id的曲目. 曲目id为: " + song["id"])
        else:
            songIdList.append(id)
            
        # Textual element check
        for text in songlistTextElementList:
            if not text in song.keys():
                print("应有的项目 \""+ text + "\" 在曲目 " + id + " 中未找到.")
            else:
                if type(song[text]) != type(" "):
                    print("项目 \"" + text + "\" 在曲目 " + id + " 中不合法, 合法值为字符串.")

        #side 
        if not "side" in song.keys():
            print("应有的项目 \"side\" is 在曲目 " + id + " 中未找到.")
        else:
            side = song["side"]
            if type(side) != type(1):
                print("项目 \"side\" 在曲目 " + id + " 中不合法, 合法值为取值0或1的整数(不带引号).")
            else:
                if side != 0 and side != 1:
                    print("项目 \"side\" 在曲目 " + id + " 中不合法, 合法值为取值0或1的整数(不带引号).")

        # Test for bg integrity
        if not standalone and checkBgIntegrity:
            if not "bg" in song.keys():
                print("应有的项目 \"bg\" 在曲目 " + id + " 中未找到.")
            else:
                bg = song["bg"]
                if bg == "":
                    if side == 0: bg = "base_light"
                    else: bg = "base_conflict"
                if not exists(bgDir + bg + ".jpg"):
                    print("曲目 " + id + " 所需的背景图片 " + bg + ".jpg 未找到.")
                if checkDiamondIntegrity:
                    if bg in diamondList:
                        diamond = diamondList[bg]
                        if diamond != "NO_DIAMOND" and not exists(bgDir + diamond + ".png"):
                            print("曲目 " + id + " 所需的diamond图片 " + diamond + ".png 未找到.")
                    elif not exists(bgDir + "diamond.png"):
                        print("曲目 " + id + " 所需的diamond图片 diamond.png 未找到.")

        # Test for packlist integrity
        if not standalone:
            if not "set" in song.keys():
                print("应有的项目 \"set\" 在曲目 " + id + " 中未找到.")
            else:
                if type(song["set"]) != type(" "):
                    print("项目 \"set\" 在曲目 " + id + " 中不合法, 合法值为字符串.")
                else:
                    if song["set"] not in packList:
                        print("曲目 " + id + " 中的项目 \"set\" 所指示的pack名称 \"" + song["set"] + "\" 在Packlist中未找到, 请检查对应关系.")

        # title_localized
        if not "title_localized" in song.keys():
            print("应有的项目 \"title_localized\" 在曲目 " + id + " 中未找到.")
        else:
            if not "en" in song["title_localized"].keys():
                print("默认英文歌曲标题(项目\"en\") 在曲目 " + id + " 中未找到.")
            else:
                for value in song["title_localized"].values():
                    if type(value) != type(" "):
                        print("Song title is not a string value for song " + id)

        # bpm_base
        if not "bpm_base" in song.keys():
            print("应有的项目 \"bpm_base\" 在曲目 " + id + " 中未找到.")
        else:
            if type(song["bpm_base"]) != type(1) and type(song["bpm_base"]) != type(1.1):
                print("项目 \"bpm_base\" 在曲目 " + id + " 中不合法, 合法值为整数或小数(不带引号)")
        
        # audioPreview & audioPreviewEnd
        audioPreviewValidity = 0

        if not "audioPreview" in song.keys():
            print("应有的项目 \"audioPreview\" 在曲目 " + id + " 中未找到.")
        else:
            if type(song["audioPreview"]) != type(1):
                print("项目 \"audioPreview\" 在曲目 " + id + " 中不合法, 合法值为整数(不带引号)")
            else:
                audioPreviewValidity += 1
        if not "audioPreviewEnd" in song.keys():
            print("应有的项目 \"audioPreviewEnd\" 在曲目 " + id + " 中未找到.")
        else:
            if type(song["audioPreviewEnd"]) != type(1):
                print("应有的项目 \"audioPreviewEnd\" 在曲目 " + id + " 中未找到.")
            else:
                audioPreviewValidity += 1
        
        if audioPreviewValidity == 2:
            if song["audioPreviewEnd"] < song["audioPreview"]:
                print("曲目 " + id + " 中, audioPreviewEnd 应当大于或等于 audioPreview.")

        # date
        if not "date" in song.keys():
            print("应有的项目 \"date\" is 在曲目 " + id + " 中未找到.")
        else:
            if type(song["date"]) != type(1):
                print("项目 \"date\" 在曲目 " + id + " 中不合法, 合法值为整数(不带引号)")

        # difficulties      
        if not "difficulties" in song.keys():
            print("应有的项目 \"difficulties\" is 在曲目 " + id + " 中未找到.")
        else:
            if not type(song["difficulties"]) == type([]):
                print("项目 \"difficulties\" 在曲目 " + id + " 中不合法, 合法值为列表(使用中括号\"[]\")")
            else:
                rating = [0,0,0,0]
                for level in song["difficulties"]:
                    for text in difficultiesTextElementList:
                        if not text in level.keys():
                            print("应有的项目 \"" + text + "\" 在曲目 " + id + " 的其中一个或多个难度中未找到.")
                        else:
                            if type(level[text]) != type(" "):
                                print("项目 \"" + text + "\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为字符串.")
                    if "hidden_until_unlocked" in level.keys():
                        if level["hidden_until_unlocked"] == True and "hidden_until" not in level.keys():
                            print("在曲目 " + id + " 的其中一个或多个难度中, 项目 \"hidden_until_unlocked\"设定为True (该曲目需要前置条件解除隐藏), \
                                但项目 \"hidden_until\" 在对应难度中未找到 (曲目对应的解锁条件未找到).")
                    if not "ratingClass" in level.keys():
                        print("应有的项目 \"ratingClass\" 在曲目 " + id + " 的其中一个或多个难度中未找到.")
                    else:
                        if type(level["ratingClass"]) != type(1):
                            print("项目 \"ratingClass\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为取值0-3之间的整数(不带引号).")
                        else:
                            if level["ratingClass"] > 3 or level["ratingClass"] < 0:
                                print("项目 \"ratingClass\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为取值0-3之间的整数(不带引号).")
                            else:
                                if rating[level["ratingClass"]] == 1:
                                    print("项目 \"ratingClass\" 在曲目 " + id + " 的不同难度中重复使用同一个值")
                                else:
                                    rating[level["ratingClass"]] = 1
                    if not "rating" in level.keys():
                        print("应有的项目 \"rating\" 在曲目 " + id + " 的其中一个或多个难度中未找到.")
                    if type(level["rating"]) != type(0):
                        print("项目 \"rating\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为整数(不带引号).")

                if rating[0:3] == [0,0,0]:
                    print("曲目" + id + "的难度不合法")
                    print("为了让Arcaea程序正确运行, 你必须在difficulties中添加Past, Present或Future(取值0-2)中的任意一个")
                    print("Beyond难度谱面无法单独存在, 否则游戏会闪退")

def checkAll():
    if useAssetsDirWhileCheckAll:
        inputAssetsDir()
    else:
        inputSongsDir()
        inputBgDir()
    print("\n开始检查Songlist中的曲目是否都存在于songs文件夹...")
    checkSonglistInFolder()
    print("\n开始检查songs文件夹中的曲目是否都存在于Songlist...")
    checkFolderInSonglist()
    print("\n开始检查songs文件夹中songs文件夹中曲目子文件夹的文件是否完整...")
    checkAssetIntegrity()
    print("\n开始检查Songlist合法性...")
    checkSonglistElement()

def scanSongDirectory():
    global directory
    if directory == "":
        directory = input("请输入你的自制包体中songs文件夹的路径 (例: C:/dir/songs/):")
        if not directory.endswith("/"):
            directory = directory + "/"
    print("正在扫描songs文件夹...")
    try:
        for root, folders, files in walk(directory, topdown=False):
            pass
    except Exception as e:
        print(repr(e))
        input()

    for eliminateName in eliminateNameList:
        if eliminateName in folders:
            folders.remove(eliminateName)
        
    return folders

def resolvePacklist():
    global directory
    if directory == "":
        directory = input("请输入你的自制包体中songs文件夹的路径 (例: C:/dir/songs/):")
    print("解析Packlist中...")
    try:
        with open(directory + "packlist", "r", encoding="UTF-8") as packListJSON:
            packlistSeq = json.loads(packListJSON.read())['packs']
    except json.JSONDecodeError as e:
        print("Packlist 解析在进行至文件第" + str(e.lineno) + "行, 第" + str(e.colno) + "列出现问题.")
        print("报错信息如下::\n" + repr(e))
        input()
        exit()
    except FileNotFoundError:
        print("没有找到有效的Packlist文件.")
        input()
        exit()
    except BaseException as e:
        print("发生了未知错误.\n" + repr(e))
        input()
        exit()
    packlist = [packListId['id'] for packListId in packlistSeq]
    packlist.append("single")
    if "epilogue" not in packlist:
        print("packlist中未找到Silent Answer曲包。这可能导致部分4.0.255及以上版本壳体无法运行。")
    return packlist

def resolveSonglist():
    global directory
    if standalone:
        directory = input("请输入你的songlist文件的路径 (例: C:/dir/songlist):")
        songlistdir = directory
    elif directory == "":
        directory = input("请输入你的自制包体中songs文件夹的路径 (例: C:/dir/songs/):")
        if not directory.endswith("/"):
            directory = directory + "/"
        songlistdir = directory + "songlist"
    else:
        songlistdir = directory + "songlist"
    print("解析Songlist中...")
    try:
        with open(songlistdir, "r", encoding="UTF-8") as songListJSON:
            songlistSeq = json.loads(songListJSON.read())['songs']
    except json.JSONDecodeError as e:
        print("Songlist解析在进行至文件第" + str(e.lineno) + "行, 第" + str(e.colno) + "列出现问题.")
        print("报错信息如下:\n" + repr(e))
        input()
        exit()
    except FileNotFoundError:
        print("没有找到有效的Songlist文件.")
        input()
        exit()
    except BaseException as e:
        print("发生了未知错误.\n" + repr(e))
        input()
        exit()
    return songlistSeq

def inputSongsDir():
    global directory
    directory = input("请输入你的自制包体中songs文件夹的路径 (例: C:/dir/songs/):")
    if not directory.endswith("/"):
        directory = directory + "/"
    return directory

def inputBgDir():
    global bgDirectory
    if bgDirectory == "":
        if useBgDirInsteadOfImgDir:
            bgDirectory = input("请输入你的自制包体中bg文件夹的路径 (例: C:/dir/bg/):")
            if not bgDirectory.endswith("/"):
                bgDirectory = bgDirectory + "/"
        else:
            bgDirectory = input("请输入你的自制包体中img文件夹的路径 (例: C:/dir/img/):")
            if not bgDirectory.endswith("/"):
                bgDirectory = bgDirectory + "/"
            bgDirectory = bgDirectory + "bg/"
    else: pass
    return bgDirectory

def inputAssetsDir():
    global directory, bgDirectory
    assetsDirectory = input("请输入你的自制包体中assets文件夹(iOS为Arc-mobile.app文件夹)的路径 (例: C:/dir/assets/):")
    if not assetsDirectory.endswith("/"):
        assetsDirectory = assetsDirectory + "/"
    if standalone:
        directory = assetsDirectory + "songs/songlist"
    else:
        directory = assetsDirectory + "songs/"
    bgDirectory = assetsDirectory + "img/bg/"
    return assetsDirectory

def checkSonglistElementWithoutBg():
    global checkBgIntegrity
    checkBgIntegrity = False
    checkSonglistElement()

def checkSonglistElementStandalone():
    global standalone
    standalone = True
    checkSonglistElement()
    
def readConfigs():
    try:
        with open("config.json", "r", encoding="utf-8") as configJSON:
            configItems = json.loads(configJSON.read())
        if "allowBydAff" in configItems:
            global allowBydAff
            allowBydAff = configItems["allowBydAff"]
        if "allowNotASCIIFileName" in configItems:
            global allowNotASCIIFileName
            allowNotASCIIFileName = configItems["allowNotASCIIFileName"]
        if "checkDiamondIntegrity" in configItems:
            global checkDiamondIntegrity
            checkDiamondIntegrity = configItems["checkDiamondIntegrity"]
        if "useAssetsDirWhileCheckAll" in configItems:
            global useAssetsDirWhileCheckAll
            useAssetsDirWhileCheckAll = configItems["useAssetsDirWhileCheckAll"]
        if "useBgDirInsteadOfImgDir" in configItems:
            global useBgDirInsteadOfImgDir
            useBgDirInsteadOfImgDir = configItems["useBgDirInsteadOfImgDir"]
        if "diamondList" in configItems:
            global diamondList
            diamondList = configItems["diamondList"]
    except:
        return 0

functions = {
    "1":checkSonglistInFolder,
    "2":checkFolderInSonglist,
    "3":checkAssetIntegrity,
    "4":checkSonglistElement,
    "5":checkSonglistElementWithoutBg,
    "6":checkSonglistElementStandalone,
    "7":checkAll,
}

print("Arcaea Songlist & 自制包完整性检查 " + version)
readConfigs()

print("1. 检查Songlist中的曲目是否都存在于songs文件夹")
print("2. 检查songs文件夹中的曲目是否都存在于Songlist")
print("3. 检查songs文件夹中曲目子文件夹的文件是否完整(aff, jpg, ogg等)")
print("4. 检查Songlist合法性(包含检查是否和Packlist等文件匹配, 以及检查背景文件完整性)")
print("5. 检查Songlist合法性(包含检查是否和Packlist等文件匹配, 不检查背景文件完整性)")
print("6. 检查Songlist合法性(仅检查Songlist本身的合法性)")
print("7. 执行全部检查")
i = input("请输入您想执行的检查项目的序号 (1-7) (默认: 7): ")
try:
    functions.get(i)()
except BaseException:
    functions.get("7")()
input("按下回车键以退出程序.")
