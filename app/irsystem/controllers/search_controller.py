from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.search import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Itinerary Planner"
net_id = "Sophie Keller: slk262, Jordana Socher: jns92, Ishika Jain: ij36,  Samantha Meakem: sam458, Nithish Kalpat: nk456 "

# @irsystem.route('/', methods=['GET'])
# def search():
# 	restaurant_query = request.args.get('restaurant')
# 	accommodation_query = request.args.get('accommodation')
# 	city = 'london' # THIS NEEDS TO BE MODIFIED TO CONTAIN CITY THAT USER IS SEARCHING
# 	restaurants = [f"{x[0]} - Score:{x[1]}" for x in getMatchings(city, "restaurant", restaurant_query)]
# 	accommodations = [f"{x[0]} - Score:{x[1]}" for x in getMatchings(city, "accommodation", accommodation_query)]
# 	output_message = "Your itinerary"
# 	if restaurants or accommodations:
# 		data = ["Restaurants"] + restaurants + ["", "Accommodations"] + accommodations
# 	else:
# 		data = []
# 	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)


@irsystem.route('/', methods=['GET'])
def search():
	restaurant_query = request.args.get('restaurant')
	accommodation_query = request.args.get('accommodation')
	attraction_query = request.args.get('attraction')
	if request.args.get('city') is not None:
		city = request.args.get('city')
		restaurants = get_matchings_cos_sim(city, "restaurant", restaurant_query)
		accommodations = get_matchings_cos_sim(city, "accommodation", accommodation_query)
		attractions = get_matchings_cos_sim(city, "attraction", attraction_query)
	else:
		city = ''
		restaurants = []
		accommodations = []
		attractions = []

	rad = within_rad(city, [x[0] for x in accommodations], [x[0] for x in restaurants], [x[0] for x in attractions], 10000)
	output_message =""# "Your itinerary options"
	data = []
	accommodations = list(filter(lambda x: rad[x[0]]['restaurants'] or rad[x[0]]['attractions'], accommodations)) #filters out accommodations w no restaurants
	for i, a in enumerate(accommodations[:5]):
		data.append([f"Itinerary #{i + 1}"])
		data.append(f"Accommodation: {a[0]}")
		data.append("Restaurants:")
		data += rad[a[0]]['restaurants'][:10]
		data.append("Attractions:")
		data += rad[a[0]]['attractions'][:10]
		data.append("")


	return render_template('search2.html', name=project_name, netid=net_id, output_message=output_message, data=data)
