from flask import request, jsonify

__all__ = ('search')

models = []


def search():
    search_string = request.args.get('q')
    if not search_string:
        return jsonify({"message": "Search string must be provided"}), 422

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    response = {}
    for model in models:
        key = "%ss" % model.__name__.lower()
        response[key] = [obj.dict() for obj in model.query.search(search_string).paginate(
            page=page, per_page=per_page, error_out=False
        ).items]
    return jsonify(response)
