"""
This module contains the resources for comments

Classes:
    CommentCollection: Not used
    CommentItem: Not used
"""

from flask import Response, request
from flask_restful import Resource
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from bikinghub.models import Comment


class CommentCollection(Resource):
    """
    Not used
    """

    def get(self):
        """
        Get all users comments
        """
        comments = Comment.query.all()
        return {"comments": [c.serialize() for c in comments]}


class CommentItem(Resource):
    """
    Not used
    """

    def get(self, comment):
        """
        Get a specific comment
        """
        comment_obj = Comment.query.get(comment).first()
        if not comment_obj:
            raise NotFound
        comment_doc = comment_obj.serialize()
        return Response(comment_doc, 200, mimetype="application/json")

    def delete(self, comment):
        """
        Delete a comment
        """
        comment_obj = Comment.query.get(comment).first()
        if not comment_obj:
            raise NotFound
        comment_obj.delete()
        return Response("Comment deleted", 200, mimetype="application/json")

    def put(self, comment):
        """
        Update a comment
        """
        if not request.json:
            raise UnsupportedMediaType
        comment_obj = Comment.query.get(comment).first()
        if not comment_obj:
            raise NotFound
        comment_obj.update(request.json)
        return Response("Comment updated", 200, mimetype="application/json")
