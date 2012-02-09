#!/usr/bin/env ruby

require 'linkeddata'

def with_context(inputfile, outputfile, contextfile)
  RDF::Reader.open(inputfile) do |reader|
    JSON::LD::Writer.open(outputfile, :context => contextfile) do |writer|
      reader.each_statement do |statement|
        writer << statement
      end
    end
  end
end

  # RDF::RDFXML::Reader.open(inputfile) do |reader|
  #   JSON::LD::Writer.open(outputfile, 
  #     :context => "context.json"
  #    ) do |writer|
  #     reader.each_statement do |statement|
  #       writer << statement
  #     end
  #   end
  # end

if __FILE__ == $0
  with_context(ARGV[0], ARGV[1], ARGV[2])
end
