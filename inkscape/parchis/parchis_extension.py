#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2020 Antonio Fijo, afijog@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Extension to create parchis game boards
See https://en.wikipedia.org/wiki/Parch%C3%ADs for more details
"""

import inkex
from inkex import Group, PathElement, Rectangle, Circle

from inkex import (
    TextElement, FlowRoot, FlowPara, Tspan, TextPath, Rectangle
)


from math import tan, radians

class ParchisEffectExtension(inkex.GenerateExtension):
    """Extension to create parchis game boards"""

    def add_arguments(self, pars):
        pars.add_argument("--useLaser", type=inkex.Boolean, help="Use laser")
        pars.add_argument("--notebook")
        pars.add_argument("--units", help="The measure units (cm/in)")

        pars.add_argument("--boardSize", type=float, help="The board size")
        pars.add_argument("--boardMargin", type=float, help="The margin size")
        pars.add_argument("--strokeWidth", type=float, help="The stroke width")

        pars.add_argument("--nPlayers", type=int, help="The number of players")
        pars.add_argument("--nColumns", type=int, help="The number of columns")
        pars.add_argument("--nBoxesPerColumn", type=int, help="The number of boxes per column")
        pars.add_argument("--generateCenter", type=inkex.Boolean, help="Generate Center")
        pars.add_argument("--generateNumbers", type=inkex.Boolean, help="Generate Numbers")

        pars.add_argument("--fillColor", type=str, help="Fill color")

    def unsignedLong(self, signedLongString):
        longColor = int(signedLongString)
        if longColor < 0:
            longColor = longColor & 0xFFFFFFFF
        return longColor

    def getColorString(self, longColor):
        longColor = self.unsignedLong(longColor)
        hexColor = hex(longColor)[2:-2]
        hexColor = hexColor.rjust(6, '0')
        return '#' + hexColor.upper()

    def generateRectangle(self, x, y, w, h, strokeWidth, stroke, fill, name):
        rect = Rectangle(x=str(x), y=str(y), width=str(w), height=str(h))
        rect.style = {'stroke': stroke, 'stroke-width': strokeWidth, 'fill': fill}
        rect.label = name
        return rect

    def generateCircle(self, x, y, r, strokeWidth, stroke, fill, name):
        circle = Circle()
        circle.center = (x,y)
        circle.radius = r
        circle.style = {'stroke': stroke, 'stroke-width': strokeWidth, 'fill': fill}
        circle.label = name
        return circle

    def generateLine(self, x1, y1, x2, y2, strokeWidth, stroke, name):
        line = PathElement()
        line.path = 'M {} {} L {} {}'.format(x1, y1, x2, y2)
        line.style = {'stroke': stroke, 'stroke-width': strokeWidth, 'fill': 'none'}
        line.label = name
        return line

    def generateText(self, text, x, y, size):
        tspan = Tspan()
        tspan.text = text

        textElement = TextElement()
        textElement.set("x", str(x))
        textElement.set("y", str(y))
        # textElement.style = "font-size:50px; font-family:Metal Lord"
        textElement.style = "font-size:{}px;".format(size)

        textElement.append(tspan)

        return textElement

    def generateSectors(self, nBoxesPerColumn, nColumns, boardSize, boardMargin, strokeWidth, stroke):
        sectors = Group.new('sectors')
        for nSector in range(self.nPlayers):
            sector = self.generateSector(nSector, nBoxesPerColumn, nColumns, boardSize, strokeWidth, stroke)
            sectors.add(sector)

        ((x1, x2), (y1, y2)) = sectors.bounding_box()
        sizeX = x2 - x1
        sizeY = y2 - y1

        sizeMinusMargin = boardSize - 2 * boardMargin
        scaleX = sizeMinusMargin / sizeX
        scaleY = sizeMinusMargin / sizeY
        sectors.transform.add_scale(scaleX, scaleY)

        translateX = -x1 + boardMargin / scaleX
        translateY = -y1 + boardMargin / scaleY
        sectors.transform.add_translate(translateX, translateY)

        return sectors

    def generateSector(self, nSector,
            nBoxesPerColumn, nColumns, size, strokeWidth, stroke):
        xBoxSize = size / 9
        yBoxSize = size / (3 * (nBoxesPerColumn-1))

        initialX = - xBoxSize * nColumns / 2.0
        initialY = yBoxSize * (nBoxesPerColumn)

        sectorName = 'sector-{}'.format(nSector+1)
        sector = Group.new(sectorName)

        def getFillColor(isHomeBox, otherColor):
            if self.useLaser:
                return 'none'
            elif isHomeBox:
                return self.sectorColors[nSector]
            else:
                return otherColor

        # Horizontal lines
        def generateHorizontalLines():
            nSectorPlusOne = nSector + 1
            lines = Group.new('hlines-{}'.format(nSectorPlusOne))
            for row in range(1, nBoxesPerColumn):
                y = initialY - yBoxSize*(row)
                name = 'hline-{}-{}'.format(nSectorPlusOne, row)
                line = self.generateLine(initialX, y, -initialX, y, strokeWidth, stroke, name)
                lines.append(line)
            return lines

        # Vertical lines
        def generateVerticalLines():
            nSectorPlusOne = nSector + 1
            lines = Group.new('vlines-{}'.format(nSectorPlusOne))
            for column in range(1, nColumns):
                x = initialX + xBoxSize*(column)
                name = 'vline-{}-{}'.format(nSectorPlusOne, column)
                line = self.generateLine(x, initialY, x, 0, strokeWidth, stroke, name)
                lines.add(line)
            return lines

        # Outline
        def generateOutline():
            pathPattern = 'm{} {} v {} l {} {} h {} l {} {} v {} Z'
            outline = PathElement()
            outline.style = {'stroke': stroke, 'stroke-width': strokeWidth, 'fill': fillSecure}
            outline.label = 'outline-{}'.format(nSector+1)

            outline.path = pathPattern.format(
                initialX, initialY,
                -initialY + yBoxSize,
                obliqueDistance, -yBoxSize,
                topDistance,
                obliqueDistance, yBoxSize,
                yBoxSize * (nBoxesPerColumn-1) )
            return outline

        # Secure Circles
        def generateSecureCircles():
            def generateSecureCircle(row, column):
                isSecureBox = getIsSecureBox(row, column)
                if (isSecureBox):
                    isHomeBox = getIsHomeBox(row, column)
                    fillSecure = getFillColor(isHomeBox, self.secureNotHomeBoxFillColor)
                    xBox = initialX + column * xBoxSize
                    yBox = initialY - (row+1) * yBoxSize
                    centerX = xBox + xBoxSize / 2
                    centerY = yBox + yBoxSize / 2
                    radius = yBoxSize * .5 / 2
                    name = 'secure-circle-{}-{}'.format(nSector+1, column)

                    circle = self.generateCircle(centerX, centerY, radius,
                        strokeWidth, stroke, fillSecure, name)
                    secureCircles.add(circle)

            secureCircles = Group.new('secure-circles-{}'.format(nSector + 1))

            row = 4
            for column in range(0, nColumns):
                generateSecureCircle(row, column)

            row = 0
            column = nColumns - 2
            generateSecureCircle(row, column)

            return secureCircles

        # Home Circle
        def generateHomeCircle():
            homeCircleX1 = -initialX
            homeCircleY1 = yBoxSize

            homeCircleY2 = initialY
            homeCircleX2 = (1/tanAngle) * (homeCircleY2 + distanceFromBoardCenter)

            mediumPointX = (homeCircleX1 + homeCircleX2) / 2
            mediumPointY = (homeCircleY1 + homeCircleY2) / 2

            r = (mediumPointX - homeCircleX1) * .9
            homeCircle = self.generateCircle(mediumPointX, mediumPointY, r,
                strokeWidth, stroke, fillSecure, 'homeCircle-{}'.format(nSector + 1))

            return homeCircle

        # Sector Center Part
        def generateSectorCenterPart():
            nSectorPlusOne = nSector + 1
            pathPattern = 'm{} {} L {} {} L {} {}'
            centerColoredPart = PathElement()
            fill = ('none', self.sectorColors[nSector])[not self.useLaser and self.generateCenter]
            centerColoredPart.style = {'stroke': stroke, 'stroke-width': strokeWidth,
                'fill': fill}
            centerColoredPart.label = 'colored-part-{}'.format(nSectorPlusOne)

            cornerSize = initialX + obliqueDistance

            centerColoredPart.path = pathPattern.format(
                cornerSize, 0,
                0, -distanceFromBoardCenter,
                -cornerSize, 0)
            return centerColoredPart

        # Sector Colored Part
        def generateSectorColoredPart():
            nSectorPlusOne = nSector + 1
            pathPattern = 'm{} {} v {} h {} v {} h {} v {} h {} v {} Z'
            coloredPart = PathElement()
            coloredPart.style = {'stroke': stroke, 'stroke-width': strokeWidth,
                'fill': self.sectorColors[nSector]}
            coloredPart.label = 'colored-part-{}'.format(nSectorPlusOne)

            coloredPart.path = pathPattern.format(
                (nColumns/2 - 2) * xBoxSize, initialY - yBoxSize,
                -initialY + yBoxSize,
                xBoxSize,
                yBoxSize * (nBoxesPerColumn-5),
                xBoxSize, yBoxSize, -xBoxSize,
                yBoxSize*3)
            return coloredPart

        isHomeBox = False
        fillSecure = getFillColor(isHomeBox, self.regularBoxFillColor)

        incAnglePerSector = 360 / self.nPlayers
        angle = 90 - incAnglePerSector / 2
        tanAngle = tan(radians(angle))
        obliqueDistance = yBoxSize / tanAngle
        topDistance = -2 * (initialX + obliqueDistance)
        distanceFromBoardCenter = tanAngle * (topDistance / 2)

        def getIsHomeBox(row, column):
            lastButColumn = column == nColumns-2
            lastColumn = column == nColumns-1
            return (lastButColumn and row >= 1) or (lastColumn and row == 4)

        def getIsSecureBox(row, column):
            lastButColumn = column == nColumns-2
            return (not lastButColumn and row == 4) or (lastButColumn and row == 0)

        def generateNumbers():
            nSectorPlusOne = nSector+1
            numbers = Group.new('numbers-{}'.format(nSectorPlusOne))
            fontSize = self.svg.unittouu(str(self.options.boardSize)) * .5

            xOffset = xBoxSize / 5
            yOffset = (yBoxSize - fontSize) / 2

            # x = xBoxSize / 2 + xOffset
            # x = (xBoxSize / 2) - (xBoxSize * (nColumns / 2)) - xOffset
            x = (xBoxSize / 2) - (xBoxSize * (nColumns / 2)) + xOffset
            y = yBoxSize - yOffset

            nNumbersPerSector = (nColumns - 1) * nBoxesPerColumn + 1

            initNumber = nNumbersPerSector * ((self.nPlayers - nSector)) - nBoxesPerColumn

            # End of board in first sector ?
            if (initNumber <= 0):
                initNumber += nNumbersPerSector

            # Next number goes up or down?
            incFactor = 1

            for column in range(0, nColumns):
                lastColumn = column == nColumns-1
                lastButColumn = column == nColumns-2

                # Last column is left aligned
                if (lastColumn):
                    x -= (xBoxSize / 2) + (xOffset / 2)

                for row in range(0, nBoxesPerColumn):
                    numberAsString = str(initNumber)
                    localXOffset = len(numberAsString) * fontSize

                    number = self.generateText(numberAsString, x, y, fontSize)
                    numbers.add(number)

                    initNumber += 1

                    # Last row in a column uses the same y for next column
                    if (row != nBoxesPerColumn -1):
                        y += incFactor * yBoxSize

                    # Last but column only has 1 number as the rest of
                    # the column is the 'home lane'
                    if (lastButColumn):
                        incFactor *= -1
                        y += incFactor * yBoxSize
                        if (nSector == 0):
                            initNumber = 1
                        break

                # Alternate up and down count
                incFactor *= -1

                # Go to next column
                x += xBoxSize

            return numbers

        # Outline
        outline = generateOutline()
        sector.add(outline)

        # Sector Colored Part
        if not self.useLaser:
            coloredPart = generateSectorColoredPart()
            sector.add(coloredPart)

        if self.generateCenter:
            centerColoredPart = generateSectorCenterPart()
            sector.add(centerColoredPart)

        # Grid of sector
        horizontalLines = generateHorizontalLines()
        sector.add(horizontalLines)

        verticalLines = generateVerticalLines()
        sector.add(verticalLines)

        # Secure Circles
        secureCircles = generateSecureCircles()
        sector.add(secureCircles)

        # Home Circle
        isHomeBox = True
        fillSecure = getFillColor(isHomeBox, self.secureNotHomeBoxFillColor)

        homeCircle = generateHomeCircle()
        sector.add(homeCircle)

        # Numbers for boxes
        if self.generateNumbers:
            numbers = generateNumbers()
            sector.add(numbers)

        # Place Sector
        sector.transform.add_translate(0, distanceFromBoardCenter)
        sector.transform.add_rotate(incAnglePerSector * nSector, 0, -distanceFromBoardCenter)
        return sector

    def generate(self):
        self.parse_arguments

        units = self.options.units
        boardSize = self.svg.unittouu(str(self.options.boardSize) + units)
        boardMargin = self.svg.unittouu(str(self.options.boardMargin) + units)

        self.useLaser = self.options.useLaser

        fill = (self.getColorString(self.options.fillColor), 'none')[self.useLaser]
        # inkex.utils.debug(fill)

        strokeWidth = self.options.strokeWidth

        sectorStroke = ('black', 'red')[self.useLaser]
        boardStroke = ('gray', 'black')[self.useLaser]

        self.sectorColors = ['yellow', 'royalblue', 'red', 'green',
                             'orange', 'hotpink', 'gold', 'darkkhaki']

        self.regularBoxFillColor = ('white', 'none')[self.useLaser]
        self.secureNotHomeBoxFillColor = 'gray'

        self.nPlayers = self.options.nPlayers
        nBoxesPerColumn = self.options.nBoxesPerColumn
        nColumns = self.options.nColumns
        self.generateCenter = self.options.generateCenter
        self.generateNumbers = self.options.generateNumbers

        # Generate Board
        board = Group.new('board')

        # Generate Border
        border = self.generateRectangle(0, 0, boardSize, boardSize, strokeWidth, boardStroke, fill, 'border')
        board.add(border)

        # Generate Sectors
        sectors = self.generateSectors(nBoxesPerColumn, nColumns,
            boardSize, boardMargin, strokeWidth, sectorStroke)
        board.add(sectors)

        return board

if __name__ == '__main__':
    ParchisEffectExtension().run()
