
all: var


var:
	fontmake -m "Piksels.designspace" -o variable --keep-overlaps --keep-direction --output-path "Piksels.ttf"

g:
	ttx -o "GSUB.ttx" -t GSUB Piksels.ttf

m:
	ttx -o "Piksels.ttf" -m Piksels.ttf GSUB.ttx