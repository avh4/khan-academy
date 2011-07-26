DOMAIN = "http://127.0.0.1:8080" || ARGV[0]

###

begin
  require 'rubygems'
  require 'mechanize'
  require 'json'
rescue LoadError => e
  puts "Run \"sudo gem install mechanize json\" to install the required gems."
  exit
end

@agent = Mechanize.new
@agent.redirect_ok = false
@exercises = JSON.parse(File.read(File.join(File.dirname(__FILE__), 'exercises.json')))

@agent.get(DOMAIN + '/_ah/login?email=test%40example.com&admin=True&action=Login&continue=http%3A%2F%2F127.0.0.1%3A8082%2F')

@exercises.each_with_index do |ex, exi|
  name = ex["name"]
  summative = ex["summative"]
  h_position = ex["h_position"]
  v_position = ex["v_position"]
  short_display_name = ex["short_display_name"]
  prerequisites = ex["prerequisites"]
  covers = ex["covers"]

  params = {
    "name" => name,
    "summative" => summative ? "1" : "",
    "h_position" => h_position,
    "v_position" => v_position,
    "short_display_name" => short_display_name,
    "live" => "1",
  }

  prerequisites.each_with_index do |prereq, i|
    params["prereq-#{i}"] = prereq
  end

  covers.each_with_index do |cover, i|
    params["cover-#{i}"] = cover
  end

  qs = Mechanize::Util.build_query_string(params)
  @page = @agent.get(DOMAIN + "/updateexercise?#{qs}")

  puts "%3d of #{@exercises.length}: #{name}" % (exi + 1)
end
