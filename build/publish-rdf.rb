#!/usr/bin/env ruby

require 'linkeddata'
require 'json'

def publish_rdf(inputfile, outputfile, contextfile)
  RDF::Reader.open(inputfile) do |reader|
    RDF::RDFXML::Writer.open(outputfile,:prefixes =>
                             get_prefixes(ARGV[2])) do |writer|
      reader.each_statement do |statement|
        writer << statement
      end
    end
  end
end

def get_prefixes(contextfile)
  ret = {}
  data = JSON.parse (File.open(contextfile, "r:utf-8").read)
  data["@context"].each_pair do |key, value|
    unless key.include? ":" then
      ret[key] = value
    end
  end

  return ret
end

if __FILE__ == $0
  publish_rdf(ARGV[0], ARGV[1], ARGV[2])
end
