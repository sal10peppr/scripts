from urlparse import urlparse as quote_plus

import requests
from bs4 import BeautifulSoup
from itertools import combinations
from json import loads
from traceback import print_exc


class Main: 

	def network_call(self, url):
		print "[GET] {0}".format(url)
		r = requests.get(url);
		return r.text

	def parse_html_and_build_tree(self, html_text):
		# Each comment has its own <tr> on hn. 
		# And further <table> elements nested in each cell 
		parsed = []
		soup = BeautifulSoup(html_text, "html.parser")
		last_found_parent = None
		count = 0
		# find each tr in <table  class="comment=tree">
		for tr in soup.find_all("tr", class_="athing"):
			count = count + 1
			# parent comments have <img> with width 0
			# child comments have <img> tags with increasing width
			# so to find if this is parent / child,
			# in each <tr>, find <img>
			img = tr.find('img')
			if img:
				if img['width'] == '0':
					# this is a parent comment
					# extracting content from this parent <tr>
					# move to separate method
					comment = self.extract_content_from_content(tr)

					# now that we have a new parent comment, record it
					last_found_parent = {
						"_element" : comment,
						"children" : [],
						"child_count" : 0}
					parsed.append(last_found_parent)
				else:
					# this is a child comment
					# extract content and add to list of children and increment child_count					
					last_found_parent["children"].append(self.extract_content_from_content(tr))
					last_found_parent["child_count"] = last_found_parent["child_count"] + 1

		print "found {0} comments...".format(count)
		
		return parsed

	# extract content from a comment <tr>
	def extract_content_from_content(self, tr):
		# this is how the tr looks now
		#print tr

		# <tr class="athing comtr " id="13257716">
		#    <td>
		#       <table border="0">
		#          <tr>
		#             <td class="ind"><img height="1" src="s.gif" width="0"/></td>
		#             <td class="votelinks" valign="top">
		#                <center>
		#                   <a href="vote?id=13257716&amp;how=up&amp;goto=item%3Fid%3D13255650" id="up_13257716">
		#                      <div class="votearrow" title="upvote"></div>
		#                   </a>
		#                </center>
		#             </td>
		#             <td class="default">
		#                <div style="margin-top:2px; margin-bottom:-10px;"><span class="comhead">
		#                   <a class="hnuser" href="user?id=wingerlang">wingerlang</a> <span class="age"><a href="item?id=13257716">4 days ago</a></span> <span id="unv_13257716"></span><span class="par"></span> <a class="togg" href="javascript:void(0)" n="1" onclick="return toggle(event, 13257716)"></a> <span class="storyon"></span>
		#                   </span>
		#                </div>
		#                <br>
		#                <div class="comment">
		#                   <span class="c00">
		#                      Speaking thai because I live there.<span>
		#                      </span>
		#                      <div class="reply">
		#                         <p><font size="1">
		#                            <u><a href="reply?id=13257716&amp;goto=item%3Fid%3D13255650%2313257716">reply</a></u>
		#                            </font>
		#                         </p>
		#                      </div>
		#                   </span>
		#                </div>
		#                </br>
		#             </td>
		#          </tr>
		#       </table>
		#    </td>
		# </tr>

		# ok this is tricky because the span has text and markup for reply
		# so lets first extract the content's parent tag which will look like this

		# <span class="c00">
		#    Speaking thai because I live there.<span>
		#    </span>
		#    <div class="reply">
		#       <p><font size="1">
		#          <u><a href="reply?id=13257716&amp;goto=item%3Fid%3D13255650%2313257716">reply</a></u>
		#          </font>
		#       </p>
		#    </div>
		# </span>
		c00 = tr.find(class_='comment').span

		# now remove the reply part which leaves us with this
		# <span class="c00">
		#    Speaking thai because I live there.<span>
		#    </span>
		# </span>
		c00.find('div').decompose()

		# we just want the text
		comment = c00.get_text().encode('utf8')
		
		return comment



if __name__ == "__main__":

	try:
		main = Main()
		# make a network call and get the content
		all_html = main.network_call("https://news.ycombinator.com/item?id=13255650")

		# parse html to a structure like this
		#[{
		# 'child_count': <no of children>, 
		# '_element': "<parent text>", 
		# 'children': [ '<first child text>', '<second child text>'] }
		# ,
		# ...
		# ]
		parsed_list = main.parse_html_and_build_tree(all_html)

		# filter out comments that have no child comments
		filtered_list = list(filter(lambda d: d['child_count'] > 0 , parsed_list))

		# sort in decending order to keep the comments with most child comments at the top
		sorted_list = sorted(filtered_list, key=lambda k : k['child_count'], reverse=True)

		# print them out
		for item in sorted_list:
			print "({0}) {1}".format(item['child_count'], item['_element'])
			for child in item['children']:
				print "    >" + child
	except Exception as e:
		print_exc()