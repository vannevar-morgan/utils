// ************************************************************
//              Name:  vann
//          Filename:  main.cpp
//           Project:  simple cli rss reader
//       
//      Date written:  Thursday, October 20, 2016
//
// ************************************************************

#include <iostream>
#include <string>
#include <sstream>
#include <utility>
#include <vector>
#include <map>
#include <cstdlib>   // for rand()
#include <ctime>     // for time to seed srand()
#include <unistd.h>  // for getpid() to seed srand()
#include <fstream>   // to manipulate the rss config file
#include <algorithm> // for binary_search(), remove()
#include <curlpp/cURLpp.hpp>
#include <curlpp/Easy.hpp>
#include <curlpp/Options.hpp>
#include <curlpp/Exception.hpp>


struct news_item{
  std::string channel_title;
  std::string title;
  std::string link;
  //  string category;
  std::string pubDate;
};

std::string get_rss_data(const std::string rss_feed);

void run_rss(const std::string& rss_config_file);

std::pair<std::string, std::string::size_type> extract_text(const std::string data, 
							    const std::string tag_begin, 
							    const std::string tag_end, 
							    const int search_begin_pos = 0, 
							    std::string::size_type search_end_pos = std::string::npos);

std::vector<news_item> parse_data(const std::string data);

void list_rss_channels(const std::string& rss_config_file);

void clear_rss_channels(const std::string& rss_config_file);

void remove_channel(const std::string& rss_config_file, const std::string& channel_name);

void add_channel(const std::string& rss_config_file, const std::string& channel_name);

std::vector<std::string> read_rss_config_file(const std::string& rss_config_file);

void write_rss_config_file(const std::string& rss_config_file, const std::string& data);

void write_rss_config_file(const std::string& rss_config_file, const std::vector<std::string>& data);




int main(int argc, char *argv[]){
  using namespace std;
  srand(time(0) + getpid());
  // if -add flag:
  //  -add channel to the channel file
  //
  // if -remove flag:
  //  -remove channel from the channel file
  //
  // if -clear flag:
  //  -clear the channel flag file
  //
  // if -list flag:
  //  -list channels in the channel file
  //
  // if no flags:
  //  -import channel names, if any
  //  -grab rss data from channels
  //  -print rss data

  string USAGE_MESSAGE = "usage: ./rss (add (url) / remove (url) / clear / list)";
  //  string rss_config_file = "/home/vann/.rss_config";
  string rss_config_file = "rss_config";

  if(argc == 1){
    run_rss(rss_config_file);
  }else if(argc == 2){
    // "clear" or "list"
    if(string(argv[1]) == "list"){
      list_rss_channels(rss_config_file);
    }else if(string(argv[1]) == "clear"){
      cout << "-delete all current rss channels...\nare you sure (y/n)?\n" << endl;
      string user_confirm;
      cin >> user_confirm;
      if(user_confirm == "y"){
	clear_rss_channels(rss_config_file);
      }
    }else{
      cout << USAGE_MESSAGE << endl;
    }
  }else if(argc == 3){
    // "add" or "remove"
    if(string(argv[1]) == "add"){
      // add channel
      string channel_name(argv[2]);
      add_channel(rss_config_file, string(argv[2]));
    }else if(string(argv[1]) == "remove"){
      //remove channel
      remove_channel(rss_config_file, string(argv[2]));
    }else{
      cout << USAGE_MESSAGE << endl;
    }
  }else{
    cout << USAGE_MESSAGE << endl;
  }
  
    
  
  
  return EXIT_SUCCESS;
}


class Open_input_file{
  // class to represent an open file for reading
public:
  Open_input_file(const std::string filename){
    m_input_file.open(filename);
  }
  
  ~Open_input_file(){
    m_input_file.close();
  }
  
  std::vector<std::string> read_lines(){
    std::vector<std::string> data;
    for(std::string line; getline(m_input_file, line);){
      data.push_back(line);
    }
    // need to reset m_input_file in case i need to read from it again...
    m_input_file.clear();
    m_input_file.seekg(0);
    return data;
  }

private:
  std::ifstream m_input_file;
};


class Open_output_file{
  // class to represent an open file for writing
public:
  Open_output_file(const char* filename, std::ios_base::openmode filemode = std::ios_base::out){
    m_output_file.open(filename, filemode);
  }
  
  ~Open_output_file(){
    m_output_file.close();
  }

  void write_lines(const std::vector<std::string> data){
    if(!data.size() == 0){
      m_output_file << data[0];
    }
    for(auto it = data.begin() + 1; it < data.end(); ++it){
      m_output_file << "\n" << *it;
    }
  }
  
  void write(const std::string data){
    m_output_file << data;
  }

private:
  std::ofstream m_output_file;
};


std::vector<std::string> read_rss_config_file(const std::string& rss_config_file){
  //
  // Read the rss config file
  //
  Open_input_file input(rss_config_file.c_str());
  std::vector<std::string> rss_channels = input.read_lines();
  return rss_channels;
}


void write_rss_config_file(const std::string& rss_config_file, const std::string& data){
  //
  // Write rss data to the rss config file
  // (use when adding a channel)
  //
  Open_output_file output(rss_config_file.c_str());
  output.write(data);
}


void write_rss_config_file(const std::string& rss_config_file, const std::vector<std::string>& data){
  //
  // Write rss data to the rss config file
  // (use when writing after erasing a channel)
  //
  Open_output_file output(rss_config_file.c_str());
  output.write_lines(data);
}




void list_rss_channels(const std::string& rss_config_file){
  //
  // Print channels listed in the rss config file
  //
  std::vector<std::string> rss_channels = read_rss_config_file(rss_config_file);
  std::cout << "rss channels list: " << std::endl;
  for(const std::string& s : rss_channels){
    std::cout << s << std::endl;
  }
}


void clear_rss_channels(const std::string& rss_config_file){
  //
  // Delete all rss channels in the rss config file
  //
  write_rss_config_file(rss_config_file,
			"");
  std::cout << "all rss channels cleared..." << std::endl;
}


void remove_channel(const std::string& rss_config_file, const std::string& channel_name){
  //
  // Remove the specified rss channel from the rss config file
  //
  std::vector<std::string> rss_channels = read_rss_config_file(rss_config_file);
  std::sort(rss_channels.begin(), rss_channels.end());
  if(std::binary_search(rss_channels.begin(), rss_channels.end(), channel_name)){
    std::vector<std::string>::iterator it = remove(rss_channels.begin(), rss_channels.end(), channel_name);
    rss_channels.erase(it, rss_channels.end());
    write_rss_config_file(rss_config_file, rss_channels);
    std::cout << "you're no longer subscribed to\n\t" << channel_name << std::endl;
  }else{
    std::cout << "you aren't subscribed to that channel..." << std::endl;
  }
}


void add_channel(const std::string& rss_config_file, const std::string& channel_name){
  //
  // Add the specified rss channel to the rss config file
  //
  
  // (should first confirm the channel name is a valid rss channel url)
  std::vector<std::string> rss_channels = read_rss_config_file(rss_config_file);
  std::sort(rss_channels.begin(), rss_channels.end());
  if(std::binary_search(rss_channels.begin(), rss_channels.end(), channel_name)){
    std::cout << "you're already subscribed to that channel..." << std::endl;
  }else{
    rss_channels.push_back(channel_name);
    std::sort(rss_channels.begin(), rss_channels.end());
    write_rss_config_file(rss_config_file, 
			  rss_channels);
    std::cout << "added channel:\n\t" << channel_name << std::endl;
  }
  //  Open_output_file output(rss_config_file.c_str(), std::ofstream::app);
}


void run_rss(const std::string& rss_config_file){
  //
  // Do an rss update:
  //   -read rss config file for urls to check
  //   -manage channel colors (add to rss config?)
  //   -get rss xml
  //   -parse rss xml for news items
  //   -print each news item
  //

  std::vector<std::string> rss_urls = read_rss_config_file(rss_config_file);

  std::map<std::string, std::string> color_map; // map channel_title to color.
  const char* color_strings[] = {"\e[91m",
				 "\e[92m",
				 "\e[93m",
				 "\e[94m",
				 "\e[95m",
				 "\e[96m"};

  for(const std::string& rss : rss_urls){
    std::string data = get_rss_data(rss);

    std::vector<news_item> channel_news = parse_data(data);

    for(const news_item& n : channel_news){
      if(color_map.find(n.channel_title) != color_map.end()){
	std::cout << color_map[n.channel_title]; // use the color for the channel if the channel has a color
      }else{
	color_map[n.channel_title] = color_strings[rand() % (sizeof(color_strings) / sizeof(color_strings[0]))];
	std::cout << color_map[n.channel_title];
      }
      std::cout << n.channel_title;
      if(n.channel_title != ""){
	std::cout << "\t";
      }
      std::cout << n.pubDate << "\n";
      std::cout << "\e[1m"; // turn on bold formatting
      std::cout << n.title << "\n";
      std::cout << "\e[21m"; // turn off bold formatting
      std::cout << "\e[4m"; // turn on underlining
      std::cout << n.link << "\n";
      std::cout << "\e[24m"; // turn off underlining
      std::cout << "\e[97m"; // reset color to white
      std::cout << std::endl;
    }    
  }
}


std::vector<news_item> parse_data(const std::string data){
  //
  // Parse rss xml for text of tags of interest.
  //
  // NOTE:
  // Consider improving in the future, not robust!!!
  // Look for something like BeautifulSoup but cpp.
  //
  // tags of interest:
  //   -item
  //   -title
  //   -link
  //   -category
  //   -pubDate
  //
  std::vector<news_item> news;
  std::string::size_type search_begin_pos = 0;

  // find channel title
  std::string::size_type search_end_pos = extract_text(data, "<item>", "</item>", search_begin_pos).second;
  std::string channel_title = extract_text(data, "<title>", "</title>", search_begin_pos, search_end_pos).first;
  search_begin_pos = search_end_pos;

  // find article title, link, category, pubDate
  while(true){
    std::pair<std::string, std::string::size_type> item_tag_data = extract_text(data, "<item>", "</item>", search_begin_pos);
    std::string item = item_tag_data.first;
    search_begin_pos = item_tag_data.second;
    if(item == ""){
      break;
    }
    news_item n;
    n.channel_title = channel_title;
    n.title = extract_text(item, "<title>", "</title>").first;
    std::string parse_cdata = extract_text(n.title, "<![CDATA[", "]]>").first;
    if(parse_cdata != ""){
      n.title = parse_cdata;
    }
    n.link = extract_text(item, "<link>", "</link>").first;
    parse_cdata = extract_text(n.link, "<![CDATA[", "]]>").first;
    if(parse_cdata != ""){
      n.link = parse_cdata;
    }
    // n.category = extract_text(item, "<category>", "</category>").first;
    // parse_cdata = extract_text(n.category, "<![CDATA[", "]]>").first;
    // if(parse_cdata != ""){
    //   n.category = parse_cdata;
    // }
    n.pubDate = extract_text(item, "<pubDate>", "</pubDate>").first;
    parse_cdata = extract_text(n.pubDate, "<![CDATA[", "]]>").first;
    if(parse_cdata != ""){
      n.pubDate = parse_cdata;
    }

    news.push_back(n);
  }
  
  return news;
}


std::pair<std::string, std::string::size_type> extract_text(const std::string data, 
							    const std::string tag_begin, 
							    const std::string tag_end, 
							    const int search_begin_pos, 
							    std::string::size_type search_end_pos){
  //
  // Parse rss xml for text of tags of interest.
  //
  // NOTE:
  // Consider improving in the future, not robust!!!
  // Look for something like BeautifulSoup but cpp.
  //
  std::string text = "";
  
  // find beginning tag
  std::string::size_type tag_begin_index = data.find(tag_begin, search_begin_pos);
  // find ending tag
  std::string::size_type tag_end_index = data.find(tag_end, tag_begin_index);
  // extract any text between the begin and end tags (but not including either tag).
  if(tag_begin_index != std::string::npos &&
     tag_end_index > tag_begin_index &&
     tag_end_index + tag_end.length() <= search_end_pos){
    text = data.substr(tag_begin_index + tag_begin.length(), 
		       tag_end_index - tag_begin_index - tag_begin.length());    
  }
  
  if(tag_end_index == std::string::npos){
    return std::pair<std::string, std::string::size_type>(text, tag_end_index);
  }else{
    return std::pair<std::string, std::string::size_type>(text, tag_end_index + tag_end.length());
  }
}


std::string get_rss_data(const std::string rss_feed){
  //
  // Return rss xml for url rss_feed.
  //
  try{
    curlpp::Cleanup cleaner;

    curlpp::Easy request;
    curlpp::options::Url url(rss_feed);
    curlpp::options::Port port(80);
    request.setOpt(url);
    request.setOpt(port);
    //    request.setOpt(new curlpp::options::ReadFunction(curlpp::types::ReadFunctionFunctor(readData)));
    //    request.perform();
    std::ostringstream os;
    os << request;
    return os.str();
  }catch(curlpp::LogicError& e){
    std::cout << e.what() << std::endl;
  }catch(curlpp::RuntimeError& e){
    std::cout << e.what() << std::endl;
  }
  return "";
}
