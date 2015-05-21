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
            
        xdiff = symbol.centerx - closestsymbol.centerx + 0.0001
        ydiff = symbol.centery - closestsymbol.centery
        angle = math.atan(ydiff/xdiff)
        if angle < -(self.anglethresh*3.14/180) and symbol.miny < closestsymbol.miny and symbol.maxy < closestsymbol.maxy:
            return "Sup", closestsymbol
        elif angle > (self.anglethresh*3.14/180) and symbol.miny > closestsymbol.miny and symbol.maxy > closestsymbol.maxy:
            if symbol.label == ",":
                return "Right", closestsymbol
            else:
                return "Sub", closestsymbol
        else:
            return "Right", closestsymbol
            
        """
        H = (closestsymbol.maxy-closestsymbol.miny)/(symbol.maxy-symbol.miny + 0.0001)
        D = (closestsymbol.centery - symbol.centery)/(closestsymbol.maxy - closestsymbol.miny + 0.0001)
        
        if symbol.miny < closestsymbol.miny and symbol.maxy > closestsymbol.miny and symbol.maxy < (closestsymbol.centery+(closestsymbol.maxy-closestsymbol.centery)/2):
            return "sup", closestsymbol
        elif symbol.maxy > closestsymbol.maxy and symbol.miny < closestsymbol.miny and symbol.miny > (closestsymbol.centery - (closestsymbol.centery-closestsymbol.miny)/2):
            if symbol.label == ",": #special case COMMA is Right
                return "Right", closestsymbol
            else:
                return "sub", closestsymbol
        else:
            return "Right", closestsymbol
        """
        
    def is_above_below_inside_single(self, symbol, neighbor):
        if symbol.centerx > neighbor.minx and symbol.centerx < neighbor.maxx:
            if symbol.centery > neighbor.miny and symbol.centery < neighbor.maxy:
                return "Inside", neighbor #symbol is inside neighbor
            else:
                if symbol.miny > neighbor.maxy:
                    return "Below", neighbor #symbol is below neighbor
                if symbol.maxy < neighbor.miny:
                    return "Above", neighbor #symbol is above neighbor
        return None, None
        
    def is_above_below_inside(self, symbol, symbolList):
        #find closest symbol that it is above, below, or inside
        closestsymbol = None
        closestrelation = None
        mindist = float('inf')
        for neighbor in symbolList: #test inside relationship first
            if neighbor.labelXML != symbol.labelXML:
                if symbol.centerx > neighbor.minx and symbol.centerx < neighbor.maxx:
                    if symbol.centery > neighbor.miny and symbol.centery < neighbor.maxy:
                        tempdist = self.dist(symbol, neighbor)
                        if tempdist < mindist:
                            mindist = tempdist
                            closestsymbol = neighbor
                            closestrelation = "Inside"
        for neighbor in symbolList:
            if neighbor.label == "-" or neighbor.label == "\sum" or neighbor.label == "\pi" or neighbor.label == "\lim":
                if (symbol.maxx > neighbor.minx and symbol.maxx < neighbor.maxx):
                    if symbol.miny > neighbor.maxy:
                        tempdist = self.dist(symbol, neighbor)
                        if tempdist < mindist:
                            mindist = tempdist
                            closestsymbol = neighbor
                            closestrelation = "Below"
                    if (0.8*symbol.maxy + 0.2*symbol.centery) < neighbor.miny: #allow for dangling strokes in g, j, p, q, y
                        tempdist = self.dist(symbol, neighbor)
                        if tempdist < mindist:
                            mindist = tempdist
                            closestsymbol = neighbor
                            closestrelation = "Above"
        return closestrelation, closestsymbol
    
    '''
    primary relationships comprise Right, Superscript, Subscript
    secondary relationships comprise Inside, Above, Below
    for each symbol a:
        if a has a primary relationship (e.g. there is a neighbor to its right)
            if a also has a secondary relationship
                if the primary neighbor shares the secondary relationship, then a has a primary relationship with the neighbor (e.g. (1+a)/2
            else 
                a has a secondary relationship (e.g. 1+a/2, a associated with / not +)
        else
            a has primary relationship
        
    -- this assumes that every symbol appears as the child of a relationship exactly once
    -- whether another symbol is a neighbor is based on bounding boxes and centroid distance
    -- a symbol may have an above/below relationship with a neighbor only if that neighbor is a division bar, summation, or product operator
    -- closest proximity is meant to handle nested cases like sqrt((y+1)/(x+2)) where y should be associated with -, not \sqrt
    
    '''
    def parse_equation(self, symbolList):
        relationlist = []
        #find root symbol, exclude it from child relationships
        #right most symbol, unless it is in an above/below relationship
        minsymbol = None
        minxcoord = float('inf')
        for symbol in symbolList:
            if symbol.minx < minxcoord:
                minxcoord = symbol.minx
                minsymbol = symbol
                
        
        secrelation, secneighbor = self.is_above_below_inside(minsymbol, symbolList)
        if secrelation is not None:
            minsymbol = secneighbor

        for symbol in symbolList:
            if symbol is not minsymbol:
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
                            relationlist.append([neighbor.labelXML, symbol.labelXML, relation])
                        else: #this symbol at root - above, below larger symbol
                            relationlist.append([secneighbor.labelXML, symbol.labelXML, secrelation])
                    else: #simple right relation
                        relationlist.append([neighbor.labelXML, symbol.labelXML, relation])
                else:
                    secrelation, secneighbor = self.is_above_below_inside(symbol, symbolList)
                    if secrelation is not None:
                        relationlist.append([secneighbor.labelXML, symbol.labelXML, secrelation])
        return relationlist