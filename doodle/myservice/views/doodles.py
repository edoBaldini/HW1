from flakon import JsonBlueprint
from flask import request, jsonify, abort
from myservice.classes.poll import Poll, NonExistingOptionException, UserAlreadyVotedException

doodles = JsonBlueprint('doodles', __name__)

_ACTIVEPOLLS = {} # list of created polls
_POLLNUMBER = 0 # index of the last created poll

@doodles.route('/doodles', methods=['POST', 'GET']) #TODO: completed
def all_polls():
    if request.method == 'POST':
        result = create_doodle(request)

    elif request.method == 'GET':
        result = get_all_doodles(request)
    return result

@doodles.route('/doodles/<int:id>',  methods=['PUT', 'DELETE', 'GET']) #TODO: completed
def single_poll(id):
    global _ACTIVEPOLLS
    result = ""
    exist_poll(id) # check if the Doodle is an existing one

    if request.method == 'GET': # retrieve a poll
        result = jsonify(_ACTIVEPOLLS[id].serialize())

    elif request.method == 'DELETE': 
        #TODO: completed, delete a poll and get back winners
        result = jsonify({'winners': _ACTIVEPOLLS[id].get_winners()})
        del _ACTIVEPOLLS[id]

    elif request.method == 'PUT': 
        vote(id, request)#TODO: completed, vote in a poll
        result = jsonify({'winners': _ACTIVEPOLLS[id].get_winners()})

    return result

@doodles.route('/doodles/<int:id>/<person>', methods=['GET', 'DELETE']) #TODO: complete the decoration
def person_poll(id, person):
    #TODO: completed, check if the Doodle exists. 
    exist_poll(id)
        
        #TODO: completed,  retrieve all preferences cast from <person> in poll <id>
    if request.method == 'GET':
        result = jsonify({'votedoptions': _ACTIVEPOLLS[id].get_voted_options(person)})

        #TODO: completed,  delete all preferences cast from <person> in poll <id>
    
    if request.method == 'DELETE':
        result = jsonify({'removed': _ACTIVEPOLLS[id].delete_voted_options(person)})

    return result
       

def vote(id, request):
    result = ""
    #TO DO: completed, extract person and option fields from the JSON request
    pool_request = request.get_json()
    person = pool_request['person']
    option = pool_request['option']
    try:
        # TODO: cast a vote from person in  _ACTIVEPOLLS[id]
        poll = _ACTIVEPOLLS[id]
        poll.vote(person, option)
    except UserAlreadyVotedException:
        abort(400) # Bad Request
    except NonExistingOptionException:
        abort(400) # Bad Request
    return result


def create_doodle(request):
    #TODO: completed, create a new poll in _ACTIVEPOLLS based on the input JSON. Update _POLLNUMBER by incrementing it.
    global _ACTIVEPOLLS, _POLLNUMBER
    pool_request = request.get_json()
    title = pool_request['title']
    options = pool_request['options']
    _POLLNUMBER += 1
    p = Poll(_POLLNUMBER, title, options)
    _ACTIVEPOLLS[p.id] = p    
    return jsonify({'pollnumber': _POLLNUMBER})



def get_all_doodles(request):
    global _ACTIVEPOLLS
    return jsonify(activepolls = [e.serialize() for e in _ACTIVEPOLLS.values()])

def exist_poll(id):
    if int(id) > _POLLNUMBER:
        abort(404) # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(id in _ACTIVEPOLLS):
        abort(410) # error 410: Gone, i.e. it existed but it's not there anymore
