# The MIT License
#
#  Copyright 2016-2017 UB Dortmund <daten.ub@tu-dortmund.de>.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import datetime
import requests
import simplejson as json
import uuid

# https://api.datacite.org/
DATACITE_API_URL = 'https://api.datacite.org/works/%s'

DATACITE_TYPES = {
    'book': 'Monograph',
    'editedbook': 'Collection',
    'bookchapter': 'Chapter',
    'bookseries': 'Series',
    'journalarticle': 'ArticleJournal',
    'article': 'ArticleJournal',
    'journalissue': 'Collection',
    'conferencepaper': 'Chapter',
    'dictionaryentry': 'Chapter',
    'encyclopediaentry': 'Chapter',
    'workingpaper': 'Report',
    'bookprospectus': 'Other',
    'bookreview': 'Other',
    'conferenceabstract': 'Other',
    'conferenceposter': 'Other',
    'conferenceprogram': 'Other',
    'isclosure': 'Other',
    'dissertation': 'Thesis',
    'fundingsubmission': 'Other',
    'license': 'Other',
    'magazinearticle': 'ArticleNewspaper',
    'manual': 'Other',
    'newsletterarticle': 'InternetDocument',
    'newspaperarticle': 'ArticleNewspaper',
    'onlineresource': 'InternetDocument',
    'patent': 'Patent',
    'registeredcopyright': 'Other',
    'researchtool': 'ResearchData',
    'supervisedstudentpublication': 'Thesis',
    'test': 'ResearchData',
    'trademark': 'Other',
    'translation': 'Other',
    'universityacademicunit': 'Thesis',
    'website': 'InternetDocument',
    'audiovisual': 'AudioVideoDocument',
    'collection': 'ResearchData',
    'dataset': 'ResearchData',
    'event': 'ResearchData',
    'image': 'ResearchData',
    'interactiveresource': 'ResearchData',
    'model': 'ResearchData',
    'physicalobject': 'ResearchData',
    'service': 'ResearchData',
    'software': 'ResearchData',
    'sound': 'ResearchData',
    'workflow': 'ResearchData',
    'other': 'Other',
    'report': 'Report',
}

DATACITE_SUBTYPES = {
    'audiovisual': 'Audiovisual',
    'collection': 'Collection',
    'dataset': 'Dataset',
    'event': 'Event',
    'image': 'Image',
    'interactiveresource': 'InteractiveResource',
    'model': 'Model',
    'physicalobject': 'PhysicalObject',
    'service': 'Service',
    'software': 'Software',
    'sound': 'Sound',
    'text': 'Text',
    'workflow': 'Workflow',
    'other': 'Other'
}

DATACITE_RELATION_TYPES = {
    'IsCitedBy': 'is_cited_by',
    'Cites': 'cites',
    'IsSupplementTo': 'is_supplement_to',
    'IsSupplementedBy': 'is_supplemented_by',
    'IsContinuedBy': 'is_continued_by',
    'Continues': 'continues',
    'IsNewVersionOf': 'is_new_version_of',
    'IsPreviousVersionOf': 'is_previous_version_of',
    'IsPartOf': 'is_part_of',
    'HasPart': 'has_part',
    'IsReferencedBy': 'is_referenced_by',
    'References': 'references',
    'IsDocumentedBy': 'is_documented_by',
    'Documents': 'documents',
    'IsCompiledBy': 'is_compiled_by',
    'Compiles': 'compiles',
    'IsVariantFormOf': 'is_variant_form_of',
    'IsOriginalFormOf': 'is_original_form_of',
    'IsIdenticalTo': 'is_identical_to',
    'HasMetadata': 'has_metadata',
    'IsMetadataFor': 'is_metadata_for',
    'Reviews': 'reviews',
    'IsReviewedBy': 'is_reviewed_by',
    'IsDerivedFrom': 'is_derived_from',
    'IsSourceOf': 'is_source_of'
}


def datacite2mms(doi=''):

    mms_json = {}

    record = requests.get(DATACITE_API_URL % doi).json()
    # print(record)

    if record.get('data'):
        if type(record.get('data')) == list:
            datacite_items = record.get('data')
        else:
            datacite_items = [record.get('data')]
    else:
        datacite_items = []

    for item in datacite_items:
        # print(item)
        if item.get('type') == 'works':
            mms_json.setdefault('id', str(uuid.uuid4()))
            timestamp = str(datetime.datetime.now())
            mms_json.setdefault('created', timestamp)
            mms_json.setdefault('changed', timestamp)
            mms_json.setdefault('editorial_status', 'new')

            if str(item.get('attributes').get('resource-type-general')).lower() == 'text':
                pubtype = DATACITE_TYPES.get(str(item.get('attributes').get('resource-type')).lower())
            elif item.get('attributes').get('resource-type-id'):
                pubtype = DATACITE_TYPES.get(str(item.get('attributes').get('resource-type-id')).lower())
            else:
                pubtype = item.get('attributes').get('resource-type-general')

            resource_type = ''
            if pubtype == 'ResearchData':
                resource_type = DATACITE_SUBTYPES.get(str(item.get('attributes').get('resource-type-id')).lower())

            mms_json.setdefault('pubtype', pubtype)
            if resource_type:
                mms_json.setdefault('resource_type', resource_type)

            title = item.get('attributes').get('title')
            mms_json.setdefault('title', title)

            issued = item.get('attributes').get('published')
            mms_json.setdefault('issued', issued)

            persons = []
            if item.get('attributes').get('author'):
                for author in item.get('attributes').get('author'):
                    person = {}
                    if author.get('literal'):
                        tmp = author.get('literal').split(' ')
                        person.setdefault('name', '%s, %s' % (tmp[len(tmp) - 1], author.get('literal').replace(' %s' % tmp[len(tmp) - 1], '')))
                    else:
                        person.setdefault('name', '%s, %s' % (author.get('family'), author.get('given')))
                    person.setdefault('role', []).append('aut')
                    persons.append(person)

            if len(persons) > 0:
                mms_json.setdefault('person', persons)

            publisher_id = item.get('attributes').get('publisher-id')

            for item1 in datacite_items:

                if item1.get('type') == 'publishers' and item1.get('id') == publisher_id:
                    mms_json.setdefault('publisher', item1.get('attributes').get('title'))

            mms_json.setdefault('DOI', []).append(doi)

            if item.get('attributes').get('description'):
                abstract = {}
                abstract.setdefault('content', item.get('attributes').get('description'))
                abstract.setdefault('shareable', True)
                mms_json.setdefault('abstract', []).append(abstract)

            related_identifiers = []
            if item.get('attributes').get('related-identifiers'):
                for relation in item.get('attributes').get('related-identifiers'):
                    identifier = relation.get('related-identifier')
                    if 'doi.org/' in relation.get('related-identifier'):
                        identifier = relation.get('related-identifier').split('doi.org/')[1]
                    related_identifier = {'related_identifier': identifier,
                                          'relation_type': DATACITE_RELATION_TYPES.get(
                                              str(relation.get('relation-type-id')))}
                    related_identifiers.append(related_identifier)

            if len(related_identifiers) > 0:
                mms_json.setdefault('related_identifiers', related_identifiers)

            break

    return mms_json

if __name__ == '__main__':

    print(json.dumps(datacite2mms('10.4230/DAGREP.1.10.37'), indent=4))
    print(json.dumps(datacite2mms('10.5162/sensor11/c1.3'), indent=4))
    print(json.dumps(datacite2mms('10.17877/DE290R-7365'), indent=4))

