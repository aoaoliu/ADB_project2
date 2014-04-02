import sys
import infobox

from Part2 import *



if __name__ == "__main__":
    if (sys.argv.__len__() != 7 or
       (sys.argv[3] != "-q" and sys.argv[3] != "-f") or
       (sys.argv[5] != "-t")) and (sys.argv.__len__() != 3):
        print("Argv format not correct!")
        print("Please use -key <Freebase API key> -q <query> -t <infobox|question>")
        print("OR")
        print("-key <Freebase API key> -f <file of queries> -t <infobox|question>")
        print("OR")
        print("-key <Freebase API key>")
        sys.exit(0)

    if sys.argv.__len__() == 7:
        queries = []
        if sys.argv[3] == "-q":
            queries.append(sys.argv[4])
        else:
            fileReader = open(sys.argv[4], "r")
            for lines in fileReader:
                lines = lines.strip()
                queries.append(lines)
            fileReader.close()

        if sys.argv[6] == "question":
            part2 = Part2()
            for eachQuery in queries:
                print("Query-Question: %s\n\n" % eachQuery)
                part2.run(eachQuery)
        else:
            for eachQuery in queries:
                print("Query-Question: %s\n\n" % eachQuery)
                infobox.infobox(eachQuery)
    else:
        while True:
            query = raw_input("Please input your query.\n")
            query = query.lower()
            print("Let me think...")
            if re.match(ur"who created .+\?$", query) is not None:
                part2 = Part2()
                part2.run(query)
            else:
                infobox.infobox(query)


    sys.exit(0)
