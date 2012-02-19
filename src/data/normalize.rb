#!/usr/bin/env ruby

require 'linkeddata'

# The normalizations done here are as follows:
#
# 1. http://purl.org/dc/elements/1.1/title is replaced with
#    http://purl.org/dc/terms/title if the object is a literal.  The
#    only difference between the two is that dcterms:title has a range
#    specified. 
#
# 2. http://purl.org/dc/elements/1.1/creator is replaced with
#    http://purl.org/dc/terms/creator if the object is not a literal.
#    The difference here is that the range for dcterms:creator is
#    dcterms:agent, which should be a resource or blank node.
#
# see:
# http://dublincore.org/usage/decisions/2010/dcterms-changes/
#
# 3. http://purl.org/dc/elements/1.1/description is replaced with
#    http://purl.org/dc/terms/description.
#
# 4. http://purl.org/dc/elements/1.1/identifier is replaced with
#    http://purl.org/dc/terms/identifier if the object is a literal.
#    The only difference between the two is that dcterms:identifier
#    has a range specified. 
#
# 5. http://purl.org/dc/elements/1.1/source is replaced with
#    http://purl.org/dc/terms/source.
#
# see:
# http://dublincore.org/usage/decisions/2008/dcterms-changes/

def normalize()
  default_titles = {}
  english_titles = {}

  dc11 = "http://purl.org/dc/elements/1.1/"
  dct = "http://purl.org/dc/terms/"

  RDF::NTriples::Writer.new() do |writer|
    RDF::NTriples::Reader.new() do |reader|
      reader.each_statement do |s|

        if s.predicate == dc11+"title" and s.object.literal?
          s.predicate = RDF::URI.new (dct+"title")
        end

        if s.predicate == dc11+"creator" and not s.object.literal?
          s.predicate = RDF::URI.new (dct+"creator")
        end

        if s.predicate == dc11+"description"
          s.predicate = RDF::URI.new (dct+"description")
        end

        if s.predicate == dc11+"identifier" and s.object.literal?
          s.predicate = RDF::URI.new (dct+"identifier")
        end

        if s.predicate == dc11+"source"
          s.predicate = RDF::URI.new (dct+"source")
        end

        if s.predicate == dct+"title"
          if s.object.has_language?
            if s.object.language.to_s.start_with?('en')
              english_titles[s.subject] = s.object.value
            end
          else
            unless s.object.value == ""
              default_titles[s.subject] = s.object.value
            end
          end
        end

        if s.object.literal?
          # some values in
          # e.g. http://creativecommons.org/licenses/sampling/1.0/rdf/
          # are CDATA encoded, when serialized their value is "" and
          # their language is lost.  This is probably a bug in RDF.rb.
          # For now just filter out the empty values.
          unless s.object.value == ""
            writer << s
          end
        else
          writer << s
        end
      end

      english_titles.each do |subj, obj|
        if not default_titles.has_key?(subj)
          p = RDF::URI.new("http://purl.org/dc/terms/title")
          writer << RDF::Statement.new(subj, p, obj)
        end
      end

    end
  end
end

if __FILE__ == $0
  normalize()
end
