import PyPDF2, os
import json


pdfReader = None
def main():
    apps = {}
    with open("res/app_save.json") as f:
            apps = json.load(f)
    inputData = {}
    if(input("New Data or Load Data (new, load)?").lower() in ["load", "l"]):
        print("-----LOADING INPUT DATA-----\n")
        inputData = loadData()
        print(inputData["file"])
        if inputData == None:
            #TODO add backup functionality
            return
    else:
        print("----RETRIEVING DATA-----\n")
        inputData = askData()

    splitPDF(inputData, apps)
    input("\n Remember to take photo of your inputs (Enter)")

def loadData():
    while 1:
        path = input("path to file (type 'quit' to quit): ")
        if path == "quit":
            print("QUITTING")
            return None
        if(os.path.isfile(path)):
            print("is a path")
            filename = path
            with open(filename) as f:
                print("opened: " + filename)
                returnobj = json.load(f)
                return returnobj
            break
        else:
            print("Not a file")

def askData():
    inputData = {
        "drawingsplit": {
            "coversheet": []
        }
    }
    #streets = input("list all roads that are in set (separate by commas please)")
    #inputData["roads"] = [x.strip() for x in streets.split(',')]
    inputData["file"] = input("Enter File Name Here ").strip()
    inputData["name"] = input("What is the project name? ").strip()
    munis = input("list all municipalities that are in set (separate by commas please) ").strip()
    inputData["munis"] = [x.strip() for x in munis.split(',')]
    counts = input("list all counties that are in set (separate by commas please) ").strip()
    inputData["counts"] = [x.strip() for x in counts.split(',')]
    #while 1:
    #    try:
    #        coversheet = input("coversheet range? (please use proper notation) ").strip()
    #        inputData["drawingsplit"]["coversheet"] = parseSplitInput(coversheet, inputData)
    #        break
    #    except IndexError as e:
    #        print(e)
    #        pass
    inputData["drawingsplit"]["coversheet"] = findCoverSheet(inputData)

    inputData["drawingsplit"]["numsplits"] = int(input("number of devisions? ").strip())
    for i in range(inputData["drawingsplit"]["numsplits"]):
        streetname = input("name of roadway " + str(i) + " ? ").strip()
        district = input("Does it reside in a Municipality, County, or GDOT (m,c,g)? ").strip().lower()
        if district == "m":
            juri = int(input("Which municipality  "+ str(inputData["munis"]) +  " (" +  str([i for i in range(len(inputData["munis"]))]) + ") ? ").strip())
            juri = inputData["munis"][juri]
            district = "Muni"

        elif district == "c":
            juri = int(input("Which Count  "+ str(inputData["counts"]) +  " (" +  str([i for i in range(len(inputData["counts"]))]) + ") ? ").strip())
            juri = inputData["counts"][juri]
            district = "Count"

        elif district == "g":
            juri = "GDOT"
            district = "\b"

        while 1:
            try:
                split = parseSplitInput(input("what is street split? (please use proper notation) ").strip(), inputData)
                break
            except Exception as e:
                print(e)
                pass
        try:
            if(juri == "GDOT"):
                inputData["drawingsplit"][juri][streetname] = split
            else:
                inputData["drawingsplit"][juri + "_" + district][streetname] = split
        except KeyError:
            if(juri == "GDOT"):
                inputData["drawingsplit"][juri] = {}
                inputData["drawingsplit"][juri][streetname] = split
            else:
                inputData["drawingsplit"][juri + "_" + district] = {}
                inputData["drawingsplit"][juri + "_" + district][streetname] = split

    if not os.path.exists(inputData["name"]+"/"):
        os.makedirs(inputData["name"]+"/")
    with open(inputData["name"]+"/" + inputData["name"] + "_input.txt", 'w') as file:
        file.write(json.dumps(inputData))
    return inputData

def splitPDF(inputData, apps):
    pdfWriter = None
    pdfFileObj = open(inputData["file"], "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict= False)

    for juri, obj in inputData["drawingsplit"].items():
        pdfWriter = None
        pdfOutFile = ""
        appPdf = None
        appReader = None
        if juri.strip() in apps:
            appPdf = open(apps[juri.strip()], "rb")
            appReader = PyPDF2.PdfFileReader(appPdf, strict= False)
        if juri == "coversheet" or juri == "numsplits":
            continue
        for road, splitset in obj.items():
            pdfWriter = PyPDF2.PdfFileWriter()

            if juri.strip() in apps:
                for pageNum in range(appReader.numPages):
                    page = appReader.getPage(pageNum)
                    pdfWriter.addPage(page)

            for split in inputData["drawingsplit"]["coversheet"]:
                for pageNum in range(split[0], split[1]+1):
                    page = pdfReader.getPage(pageNum)
                    pdfWriter.addPage(page)
            for split in splitset:
                for pageNum in range(split[0], split[1]+1):
                    page = pdfReader.getPage(pageNum)
                    pdfWriter.addPage(page)
            print(juri.strip(),"/",road.strip(),"/ATL_",inputData["name"].strip(),"_",juri.strip(),"_",road.strip(),"_app.pdf<",splitset,">" )
            pdfOutFileAddress = inputData["name"] + "/"+juri.strip() + "/" + road.strip() + "/"
            pdfOutFileName = inputData["name"] + "/" + juri.strip() + "/" + road.strip() + "/ATL_"+ inputData["name"].strip() + "-" + juri.strip() + "-" + road.strip() + "_app.pdf"
            if not os.path.exists(pdfOutFileAddress):
                os.makedirs(pdfOutFileAddress)
            else:
                if(input("Do you want to delete old files (y/n)?").lower() in ["y", "yes"]):
                    print("OVERWRITING FILES")
                    shutil.rmtree(pdfOutFileAddress)
                    os.makedirs(pdfOutFileAdress)
                else:
                    print("ABORTING")
                    return
            pdfOutFile = open(pdfOutFileName, 'wb')
            pdfWriter.write(pdfOutFile)
            pdfOutFile.close()
    pdfFileObj.close()


def parseSplitInput(string, inputData):
    pdfFileObj = open(inputData["file"], "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
    returnobj = []
    ranges = [x.strip() for x in string.split(',')]
    for r in ranges:
        spread = [int(x.strip()) for x in r.split(':') ]
        if(spread[0]<0 or spread[1]<0 or spread[0]-spread[1] > 0 or spread[1] >= pdfReader.numPages):
            raise IndexOutOfBoundException("Negative Values is not allowed")
        returnobj.append(spread)
    pdfFileObj.close
    return returnobj

def findCoverSheet(inputData):
    pdfFileObj = open(inputData["file"], "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
    csindex = -1
    skindex = -1
    for page in range(pdfReader.numPages):
        text = pdfReader.getPage(page).extractText()
        if("CONTACT SHEET" in text and "TABLE OF CONTENTS" not in text and "GENERAL NOTES" not in text):
            print("Found Contact Sheet at Page: " + str(page))
            csindex = page
        if("SYMBOLS KEY" in text and "TABLE OF CONTENTS" not in text):
            print("Found Symbols Sheet at Page: " + str(page))
            skindex = page
        if(csindex >0 and skindex >0):
            break
    return [[0, csindex], [skindex, skindex]]


if __name__ == "__main__":
    main()
