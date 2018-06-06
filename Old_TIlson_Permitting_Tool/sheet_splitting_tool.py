import PyPDF2, os

inputData = {
    #"roads": [],
    "working_directory": "",
    "name": "",
    "file": "",
    "munis": [],
    "counts": [],
    "drawingsplit": {
        "coversheet":[[0,3], [6,7]],
        "numsplits": 0
    }
}
pdfReader = None
def main():
    getData()
    splitPDF()

def getData():
    #streets = input("list all roads that are in set (separate by commas please)")
    #inputData["roads"] = [x.strip() for x in streets.split(',')]
    inputData["file"] = input("Enter File Name Here ").strip()
    inputData["name"] = input("What is the project name? ").strip()
    munis = input("list all municipalities that are in set (separate by commas please) ").strip()
    inputData["munis"] = [x.strip() for x in munis.split(',')]
    counts = input("list all counties that are in set (separate by commas please) ").strip()
    inputData["counts"] = [x.strip() for x in counts.split(',')]
    while 1:
        try:
            coversheet = input("coversheet range? (please use proper notation) ").strip()
            inputData["drawingsplit"]["coversheet"] = parseSplitInput(coversheet)
            break
        except Exception as e:
            print(e)
            pass

    inputData["drawingsplit"]["numsplits"] = int(input("number of devisions? ").strip())
    for i in range(inputData["drawingsplit"]["numsplits"]):
        streetname = input("name of roadway " + str(i) + " ? ").strip()
        district = input("Does it reside in a Municipality or County (m,c)? ").strip().lower()
        if district == "m":
            juri = int(input("Which municipality  "+ str(inputData["munis"]) +  " (" +  str([i for i in range(len(inputData["munis"]))]) + ") ? ").strip())
            juri = inputData["munis"][juri]
            district = "Muni"
            #count = "Nan"
        elif district == "c":
            juri = int(input("Which Count  "+ str(inputData["counts"]) +  " (" +  str([i for i in range(len(inputData["counts"]))]) + ") ? ").strip())
            juri = inputData["counts"][juri]
            district = "Count"
            #muni = "Nan"
        while 1:
            try:
                split = parseSplitInput(input("what is street split? (please use proper notation) ").strip())
                break
            except Exception as e:
                print(e)
                pass
        try:
            inputData["drawingsplit"][juri + "_" + district][streetname] = split
        except KeyError:
            inputData["drawingsplit"][juri + "_" + district] = {}
            inputData["drawingsplit"][juri + "_" + district][streetname] = split
    print(inputData)

def splitPDF():
    pdfWriter = None
    pdfFileObj = open(inputData["file"], "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    for juri, obj in inputData["drawingsplit"].items():
        pdfWriter = PyPDF2.PdfFileWriter()
        pdfOutFile = ""
        if juri == "coversheet" or juri == "numsplits":
            continue
        for road, splitset in obj.items():
            for split in inputData["drawingsplit"]["coversheet"]:
                for pageNum in range(split[0], split[1]+1):
                    page = pdfReader.getPage(pageNum)
                    pdfWriter.addPage(page)
            for split in splitset:
                for pageNum in range(split[0], split[1]+1):
                    page = pdfReader.getPage(pageNum)
                    pdfWriter.addPage(page)
            print(juri.strip(),"/",road.strip(),"/ATL_",inputData["name"].strip(),"_",juri.strip(),"_",road.strip(),"_app.pdf<",splitset,">" )
            pdfOutFileAddress = juri.strip() + "/" + road.strip() + "/"
            pdfOutFileName = juri.strip() + "/" + road.strip() + "/ATL_"+ inputData["name"].strip() + "-" + juri.strip() + "-" + road.strip() + "_app.pdf"
            if not os.path.exists(pdfOutFileAddress):
                os.makedirs(pdfOutFileAddress)
            pdfOutFile = open(pdfOutFileName, 'wb')
            pdfWriter.write(pdfOutFile)
            pdfOutFile.close()
    pdfFileObj.close()





def parseSplitInput(string):
    pdfFileObj = open(inputData["file"], "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    returnobj = []
    ranges = [x.strip() for x in string.split(',')]
    for r in ranges:
        spread = [int(x.strip()) for x in r.split(':') ]
        if(spread[0]<0 or spread[1]<0 or spread[0]-spread[1] > 0 or spread[1] >= pdfReader.numPages):
            raise IndexOutOfBoundException("Negative Values is not allowed")
        returnobj.append(spread)
    pdfFileObj.close
    return returnobj

if __name__ == "__main__":
    main()
