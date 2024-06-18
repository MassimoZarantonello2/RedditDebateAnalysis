class RedditResponse:
    comment_id = '-1'
    comment_body = ''
    comment_author_id = '-1'
    comment_author_name = ''
    comment_parent_id = '-1'
    comment_parten_name = ''
    comment_posted_time = ''
    comment_score = 0


    def __init__(self, comment_id, comment_body, comment_author_id, comment_author_name, comment_parent_id, comment_parten_name, comment_posted_time, comment_score):
        self.comment_id = comment_id
        self.comment_body = comment_body
        self.comment_author_id = comment_author_id
        self.comment_author_name = comment_author_name
        self.comment_parent_id = comment_parent_id
        self.comment_parten_name = comment_parten_name
        self.comment_posted_time = comment_posted_time
        self.comment_score = comment_score

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'comment_body': self.comment_body,
            'comment_author_id': self.comment_author_id,
            'comment_author_name': self.comment_author_name,
            'comment_parent_id': self.comment_parent_id,
            'comment_parten_name': self.comment_parten_name,
            'comment_posted_time': self.comment_posted_time,
            'comment_score': self.comment_score
        }