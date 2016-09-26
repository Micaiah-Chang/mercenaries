from collections import defaultdict, namedtuple

from bs4 import BeautifulSoup, Tag

from utils import unescape as entity_unescape

BoldCollection = namedtuple("BoldCollection", 'post_number bold')


def iterate_through_posts(filename):
    with open(filename) as f_doc:
        html_doc = f_doc.read()
        soup = BeautifulSoup(html_doc, "html.parser")

    post_iter = soup.find_all("div", {"class": "msg_infobox"})

    collected_user_bolds = defaultdict(list)

    # Find every post via its message header
    for header in post_iter:
        current_user, post_number = parse_html_header(header)

        if current_user is None:
            continue

        post_body = header.next_sibling
        quoteless_post_body = remove_quotes(post_body)
        sigless_post_body = remove_signatures(quoteless_post_body)
        user_bolds = bold_in_post(sigless_post_body)

        merge_user_bolds(collected_user_bolds, current_user, post_number, user_bolds)

    return collected_user_bolds

def merge_user_bolds(collected_bolds, current_user, post_number, user_bolds):
    if user_bolds:
        bold_collection = map(lambda bold: BoldCollection(post_number, bold), user_bolds)
        collected_bolds[current_user].extend(bold_collection)
    else:
        pass

def bold_in_post(post):

    collected_bold = [tag for tag in post.find_all('b')]
    return collected_bold


def parse_html_header(header):
    '''Find post number and username from message header.
    HTML from 05/14/2014'''
    if "deleted" in header["class"]:
        return None, None

    user_name = header.select("a.name")[0].get_text()

    post_no_txt = header.select("span.message_num")[0].get_text()
    post_no = int(post_no_txt[1:])  # remove hashmark and convert to number

    return user_name, post_no

def remove_quotes(post):
    '''Removes quoted messages from post'''
    for tag in post.descendants:
        if isinstance(tag, Tag) and tag.blockquote is not None:
            tag.blockquote.extract()
    return post

def remove_signatures(post):
    for tag in post.descendants:
        if (isinstance(tag, Tag) and (tag.div is not None) and
            (tag.div.attrs is not None) and
            ('signature' in tag.div.attrs.get('class', []))):
            tag.div.decompose()

    return post


def serialize_bold_collection(bold_collection):
    post_number = bold_collection.post_number
    bold = bold_collection.bold.__str__()

    result_string = 'Post Number: %d\n%s\n' % (post_number, entity_unescape(bold))
    return result_string

def write_to_file(result_filename, collected_bold_dict):
    if not collected_bold_dict:
        return

    result_string = ''
    for user, bold_collections in collected_bold_dict.iteritems():
        stringified_bold_collection = map(serialize_bold_collection, bold_collections)
        bold_collection_result = '\n'.join(stringified_bold_collection)
        result_row = "User: %s\n%s" % (user, bold_collection_result)
        result_string += result_row + '\n\n---\n\n'

    with open(result_filename, 'w') as txt_file:
        txt_file.write(result_string)


def main():
    page_files = ["topic/%d.html" % x for x in range(11)]
    result_files = ["result/%d.txt" % x for x in range(11)]

    collected_bolds = map(iterate_through_posts, page_files)

    entries = zip(result_files, collected_bolds)
    map(lambda args: write_to_file(*args), entries)

if __name__ == '__main__':
    main()
