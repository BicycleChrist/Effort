from FinanceFuckAround import *

WantedKeys = {
    "INCOME_STATEMENT" : ["grossProfit", "netIncome"],
    "BALANCE_SHEET" : ["commonStockSharesOutstanding", "retainedEarnings", "longTermDebt", "totalAssets", "deferredRevenue"]
}

## these maps are laid out as denominator : list[numberator]
WantedPercentages = {
    "BALANCE_SHEET" : {
        "totalAssets" : ["totalCurrentAssets", "inventory", "propertyPlantEquipment",],
        "longTermDebt" : ["currentDebt",],
        "totalLiabilities" : ["totalCurrentLiabilities",],
    },
    "INCOME_STATEMENT" : {
        "totalRevenue" : ["grossProfit", "operatingExpenses",],
        "incomeBeforeTax" : ["incomeTaxExpense",],
    },
    "CASH_FLOW" : {
        "operatingCashflow" : ["netIncome",],
    },
}

KeyFormattingExcluded = ["fiscalDateEnding", "reportedCurrency"]


def OutputName(ticker, statement_type):
    name = f"{ticker}_{statement_type}_calc.txt"
    calcpath = str(CalcFolder) + name
    return calcpath

def LoadJSON_FromComponents(ticker=default_ticker, statement_type=default_statementtype):
    filename = GetFilename(ticker, statement_type)
    print("loading JSON from: ", filename)
    with open(filename) as file:
        data = json.load(file)
    return data
    
def LoadJSON_FromFilename(theFilename):
    print("loading JSON from: ", theFilename)
    with open(theFilename) as file:
        data = json.load(file)
    return data

# the JSON structure for income statements is:
# Symbol:str, Annual_Reports:list[dict], Quarterly_Reports:list[dict]
# the reports are lists where each entry represents the data for that year / quarter

def PrintKeys(ticker=default_ticker, statement_type=default_statementtype):
    data = LoadJSON_FromComponents(ticker, statement_type)
    wanted = WantedKeys.setdefault(statement_type, [])
    if len(wanted) == 0: return
    print("-" * 55)
    for report in data["annualReports"]:
        print(report["fiscalDateEnding"])
        for key in wanted:
            value = report[key]
            if value == "None" : print(f"{key} : ${0}")
            else: print(f"{key} : ${'{:,.2f}'.format(int(value))}")
    print('\n')

# it's actuallly easier to just print everything
def PrintAllKeys(ticker, statement_type):
    data = LoadJSON_FromComponents(ticker, statement_type)
    for report in data["annualReports"]:
        for key, value in report.items():
            if key in KeyFormattingExcluded: print(f"{key} : {value}"); continue;
            if value == "None": print(f"{key} : ${0}"); continue;
            print(f"{key} : ${'{:,.2f}'.format(int(value))}")
        print('\n')

def CalculatePercentages(data):
    Calc_Dict:dict = {}
    dictname = data["symbol"] + "_" + data["StatementType"] + "_annualReports"
    Calc_Dict.update({"dictname" : dictname})
    ToCalc = WantedPercentages[data["StatementType"]]
    if len(ToCalc) == 0 : return
    for Rep in data["annualReports"]:
        Results = []
        def AsPercentage(fieldOne, fieldTwo):
            if Rep[fieldOne] == "None" or Rep[fieldTwo] == "None":
                return "None"
            thenumber = float(Rep[fieldOne]) / float(Rep[fieldTwo]) * 100
            return f"{fieldOne} = {thenumber:.3f}% of {fieldTwo}"
        for denominator, FieldOneList in ToCalc.items():
            for FieldOne in FieldOneList:
                Results.append(AsPercentage(FieldOne, denominator))
        Calc_Dict.update({Rep["fiscalDateEnding"] : Results})
    return Calc_Dict

def CreateCalcsFor(tickersToUse):
    for T in tickersToUse:
        filenames = TickerMap[T]
        for N in filenames:
            data = LOADED_FILES[N]
            print(N)
            Calcs = CalculatePercentages(data)
            pprint.pprint(Calcs)
            print('\n')


PrintKeys("NVDA")
PrintKeys("MSFT", "BALANCE_SHEET")
PrintAllKeys("AMD", "INCOME_STATEMENT")

wanted_calcs = ["MSFT", "NVDA", "EXTR"]
CreateCalcsFor(wanted_calcs)