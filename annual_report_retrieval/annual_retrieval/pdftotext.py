from subprocess import call
import os

def pdftotext(ch_save_path, en_save_path, ch_converted_path, en_converted_path):

	c_list = os.listdir(ch_save_path)
	e_list = os.listdir(en_save_path)

	for path in [ch_converted_path, en_converted_path]:
		if not os.path.exists(path):
			os.makedirs(path)

	for each in c_list:

		call('pdftotext ' + os.path.join(ch_save_path, each) + ' ' + os.path.join(ch_converted_path, each[:-4]), shell = True)
		print ('pdftotext ' + os.path.join(ch_save_path, each) + ' ' + os.path.join(ch_converted_path, each[:-4]))

	for each in e_list:

		call('pdftotext ' + os.path.join(en_save_path, each) + ' ' + os.path.join(en_converted_path, each[:-4]), shell = True)
		print ('pdftotext ' + os.path.join(en_save_path, each) + ' ' + os.path.join(en_converted_path, each[:-4]))