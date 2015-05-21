import math

class Equationparser():
    def __init__(self):
        self.anglethresh = 20
        
    def dist(self, symbol1, symbol2):
        x1 = symbol1.centerx
        y1 = symbol1.centery
        x2 = symbol2.centerx
        y2 = symbol2.centery
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
    
    def is_right_super_sub(self, symbol, symbolList):
        #extract closest symbol to the right of symbolList
        closestsymbol = None
        mindist = float('inf')
        for neighbor in symbolList:
            if neighbor.centerx < symbol.centerx and neighbor.labelXML != symbol.labelXML:
                tempdist = self.dist(neighbor, symbol)
                if tempdist < mindist:
                    mindist = tempdist
                    closestsymbol = neighbor
        if closestsymbol is None:
            return None, None
            
        '''xdiff = symbol.centerx - closestsymbol.centerx
        ydiff = symbol.centery - closestsymbol.centery
        angle = math.atan(ydiff/xdiff)
        if angle < -(self.anglethresh*3.14/180):
            return "sub", closestsymbol
        elif angle > (self.anglethresh*3.14/180):
            return "sup", closestsymbol
        else:
            return "right", closestsymbol'''
            
        H = (closestsymbol.maxy-closestsymbol.miny)/(symbol.maxy-symbol.miny + 0.0001)
        D = (closestsymbol.centery - symbol.centery)/(closestsymbol.maxy - closestsymbol.miny + 0.0001)
        
        if symbol.miny < closestsymbol.miny and symbol.maxy > closestsymbol.miny and symbol.maxy < (closestsymbol.centery+(closestsymbol.maxy-closestsymbol.centery)/2):
            return "sup", closestsymbol
        elif symbol.maxy > closestsymbol.maxy and symbol.miny < closestsymbol.miny and symbol.miny > (closestsymbol.centery - (closestsymbol.centery-closestsymbol.miny)/2):
            if symbol.label == "COMMA": #special case COMMA is right
                return "right", closestsymbol
            else:
                return "sub", closestsymbol
        else:
            return "right", closestsymbol
    
    def is_above_below_inside_single(self, symbol, neighbor):
        if symbol.centerx > neighbor.minx and symbol.centerx < neighbor.maxx:
            if symbol.centery > neighbor.miny and symbol.centery < neighbor.maxy:
                return "inside", neighbor #symbol is inside neighbor
            else:
                if symbol.miny > neighbor.maxy:
                    return "below", neighbor #symbol is below neighbor
                if symbol.maxy < neighbor.miny:
                    return "above", neighbor #symbol is above neighbor
        return None, None
        
    def is_above_below_inside(self, symbol, symbolList):
        #find closest symbol that it is above, below, or inside
        closestsymbol = None
        closestrelation = None
        mindist = float('inf')
        for neighbor in symbolList:
            if neighbor.labelXML != symbol.labelXML:
                if symbol.centerx > neighbor.minx and symbol.centerx < neighbor.maxx:
                    if symbol.centery > neighbor.miny and symbol.centery < neighbor.maxy:
                        closestsymbol = neighbor
                        closestrelation = "inside"
                    else:
                        if symbol.miny > neighbor.maxy:
                            closestsymbol = neighbor
                            closestrelation = "below"
                        if symbol.maxy < neighbor.miny:
                            closestsymbol = neighbor
                            closestrelation = "above"
        return closestrelation, closestsymbol
        
    
    def parse_equation(self, symbolList):
        relationlist = []
        for symbol in symbolList:
            #if a is to the right, super, or sub
                #if there is a line symbol that a is above or below
                    #if the other symbol is also above or below line symbol, 
                        #return this symbol right of that symbol
                    #else return this symbol above or below line symbol
                #else this symbol right, super or sub that symbol
            #if a is not to the right of anything, evaluate inside, above, below
            #if a is nothing, return nothing (omit from output)
            
            #needed helper functions
            #check whether a is right, super, or sub, return rel and other symbol
            #check whether a is above, below, or inside another function, return rel and other symbol
            
            relation, neighbor = self.is_right_super_sub(symbol, symbolList)
            if relation is not None:
                secrelation, secneighbor = self.is_above_below_inside(symbol, symbolList) #e.g. a divide sign or summation sign
                if secrelation is not None:
                    secrelation2, secneighbor2 = self.is_above_below_inside_single(neighbor, secneighbor)
                    if secrelation == secrelation2: #e.g., to right of something, but both symbols nested
                        relationlist.append([neighbor.labelXML, symbol.labelXML, "right"])
                    else: #this symbol at root - above, below larger symbol
                        relationlist.append([secneighbor.labelXML, symbol.labelXML, secrelation])
                else: #simple right relation
                    relationlist.append([neighbor.labelXML, symbol.labelXML, relation])
            else:
                secrelation, secneighbor = self.is_above_below_inside(symbol, symbolList)
                if secrelation is not None:
                    relationlist.append([secneighbor.labelXML, symbol.labelXML, secrelation])
        return relationlist