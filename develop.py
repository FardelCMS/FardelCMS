from fardel import Fardel

fardel = Fardel(develop=True)

if __name__ == "__main__":
	fardel.app.run(host='0.0.0.0')