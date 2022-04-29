# Arcaea Songlist & Package Integrity Checker
# 
# Version: 1.3-CHS
# 
# Last Edited: April 29 2022
#
# Distributed Under the GPLv3 Lisence: https://www.gnu.org/licenses/gpl-3.0.en.html
#
# 1.3 Update:
#
# Fixed dublicate loop run when checking assets integrity.
# The program will now run with python.exe (removed exit() in the program).
# Added Windows .EXE execution version.
#
# To-dos:
# bg check not implemented
# Increase readibility

from os import walk
import json
from re import match

version = "1.3-CHS"

fileList = ["base.jpg","base_256.jpg","base.ogg"]

eliminateNameList = ["random","pack","tutorial"]

songlistTextElementList = ["artist","bpm","version", "purchase","bg","set"]
songlistNumElementList = ["bpm_base"]

difficultiesTextElementList = ["chartDesigner", "jacketDesigner"]

standalone = False

directory = ""

def checkSonglistInFolder():
    dirs = scanSongDirectory()
    songList = resolveSonglist()
    for song in songList:
        for songFolderName in dirs:
            if song['id'] in dirs or ("dl_" + song['id']) == songFolderName:
                return 0
        print("id 为 " + song['id'] + " 的曲目在songlist中, 但不在文件夹中")

def checkFolderInSonglist():
    dirs = scanSongDirectory()
    songList = resolveSonglist()
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
        if songFolderName.startswith("dl_"):
            print("跳过下载文件夹 " + songFolderName)
            continue
        for rootS, dirsS, filesS in walk(directory + "/" + songFolderName, topdown=False):
            pass
        for checkObj in fileList:
            if checkObj not in filesS:
                print("在文件夹 " + songFolderName + " 中没有找到有效的" + checkObj + " 文件.")
        withAff = False
        for aff in filesS:
            if match("[0-2].aff", aff) != None:
                withAff = True
        if not withAff:
            print("在文件夹 " + songFolderName + " 中没有找到有效的谱面(.aff)文件.")

def checkSonglistElement():
    songList = resolveSonglist()
    if not standalone:
        packList = resolvePacklist()
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

        # Test for bg integrity


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

        #title_localized
        if not "title_localized" in song.keys():
            print("应有的项目 \"title_localized\" 在曲目 " + id + " 中未找到.")
        else:
            if not "en" in song["title_localized"].keys():
                print("默认英文歌曲标题(项目\"en\") 在曲目 " + id + " 中未找到.")
            else:
                for value in song["title_localized"].values():
                    if type(value) != type(" "):
                        print("Song title is not a string value for song " + id)

        #bpm_base
        if not "bpm_base" in song.keys():
            print("应有的项目 \"bpm_base\" 在曲目 " + id + " 中未找到.")
        else:
            if type(song["bpm_base"]) != type(1) and type(song["bpm_base"]) != type(1.1):
                print("项目 \"bpm_base\" 在曲目 " + id + " 中不合法, 合法值为整数或小数(不带括号)")
        
        # audioPreview & audioPreviewEnd
        audioPreviewValidity = 0

        if not "audioPreview" in song.keys():
            print("应有的项目 \"audioPreview\" 在曲目 " + id + " 中未找到.")
        else:
            if type(song["audioPreview"]) != type(1):
                print("项目 \"audioPreview\" 在曲目 " + id + " 中不合法, 合法值为整数(不带括号)")
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
        
        #side 
        if not "side" in song.keys():
            print("应有的项目 \"side\" is 在曲目 " + id + " 中未找到.")
        else:
            if type(song["side"]) != type(1):
                print("项目 \"side\" 在曲目 " + id + " 中不合法, 合法值为取值0或1的整数(不带括号).")
            else:
                if song["side"]!= 0 and song["side"]!= 1:
                    print("项目 \"side\" 在曲目 " + id + " 中不合法, 合法值为取值0或1的整数(不带括号).")

        #date
        if not "date" in song.keys():
            print("应有的项目 \"date\" is 在曲目 " + id + " 中未找到.")
        else:
            if type(song["date"]) != type(1):
                print("项目 \"date\" 在曲目 " + id + " 中不合法, 合法值为整数(不带括号)")
        
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
                            print("应有的项目 \"" + text + "\" is 在曲目 " + id + " 的难度列表中未找到.")
                        else:
                            if type(level[text]) != type(" "):
                                print("项目 \"" + text + "\" 在曲目 " + id + " 中不合法, 合法值为字符串.")
                    if not "ratingClass" in level.keys():
                        print("应有的项目 \"ratingClass\" 在曲目 " + id + " 的其中一个或多个难度中未找到.")
                    else:
                        if type(level["ratingClass"]) != type(1):
                            print("项目 \"ratingClass\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为取值0-3之间的整数(不带括号).")
                        else:
                            if level["ratingClass"] > 3 or level["ratingClass"] < 0:
                                print("项目 \"ratingClass\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为取值0-3之间的整数(不带括号).")
                            else:
                                if rating[level["ratingClass"]] == 1:
                                    print("项目 \"ratingClass\" 在曲目 " + id + " 中多次重复同一个值")
                                else:
                                    rating[level["ratingClass"]] = 1
                    if not "rating" in level.keys():
                        print("应有的项目 \"rating\" 在曲目 " + id + " 的其中一个或多个难度中未找到.")
                    if type(level["rating"]) != type(0):
                        print("项目 \"rating\" 在曲目 " + id + " 的其中一个或多个难度中不合法, 合法值为整数(不带括号).")

                if rating[0:3] == [0,0,0]:
                    print("曲目" + id + "的难度不合法")
                    print("为了让Arcaea程序正确运行, 你必须在difficulties中添加Past, Present或Future(取值0-2)中的任意一个")
                    print("Beyond难度谱面无法单独存在, 否则游戏会闪退")

def checkAll():
    checkSonglistInFolder()
    checkFolderInSonglist()
    checkAssetIntegrity()
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
    except FileNotFoundError:
        print("没有找到有效的Packlist文件.")
        input()
    except BaseException as e:
        print("发生了未知错误.\n" + repr(e))
        input()
    packlist = [packListId['id'] for packListId in packlistSeq]
    packlist.append("single")
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
    except FileNotFoundError:
        print("没有找到有效的Songlist文件.")
        input()
    except BaseException as e:
        print("发生了未知错误.\n" + repr(e))
        input()
    return songlistSeq

def checkSonglistElementStandalone():
    global standalone
    standalone = True
    checkSonglistElement()
    


functions = {
    "1":checkSonglistInFolder,
    "2":checkFolderInSonglist,
    "3":checkAssetIntegrity,
    "4":checkSonglistElement,
    "5":checkSonglistElementStandalone,
    "6":checkAll,
}

print("Arcaea Songlist & 自制包完整性检查 " + version)

print("1. 检查Songlist中的曲目是否都存在于songs文件夹")
print("2. 检查songs文件夹中的曲目是否都存在于Songlist")
print("3. 检查songs文件夹中曲目子文件夹的文件是否完整(aff, jpg, ogg等)")
print("4. 检查Songlist合法性(包含检查是否和Packlist等文件匹配)")
print("5. 检查Songlist合法性(仅检查Songlist本身的合法性)")
print("6. 执行全部检查")
i = input("请输入您想执行的检查项目的序号 (1-6): ")

functions.get(i)()

input("按下回车键以退出程序.")
