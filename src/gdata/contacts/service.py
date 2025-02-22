#!/usr/bin/env python
#
# Copyright 2009 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ContactsService extends the GDataService for Google Contacts operations.

  ContactsService: Provides methods to query feeds and manipulate items.
                   Extends GDataService.

  DictionaryToParamList: Function which converts a dictionary into a list of
                         URL arguments (represented as strings). This is a
                         utility function used in CRUD operations.
"""

from __future__ import absolute_import
__author__ = 'dbrattli (Dag Brattli)'


import gdata
import gdata.calendar
import gdata.service


DEFAULT_BATCH_URL = ('http://www.google.com/m8/feeds/contacts/default/full'
                     '/batch')
DEFAULT_PROFILES_BATCH_URL = ('http://www.google.com'
                              '/m8/feeds/profiles/default/full/batch')

GDATA_VER_HEADER = 'GData-Version'


class Error(Exception):
  pass


class RequestError(Error):
  pass


class ContactsService(gdata.service.GDataService):
  """Client for the Google Contacts service."""

  def __init__(self, email=None, password=None, source=None,
               server='www.google.com', additional_headers=None,
               contact_list='default', **kwargs):
    """Creates a client for the Contacts service.

    Args:
      email: string (optional) The user's email address, used for
          authentication.
      password: string (optional) The user's password.
      source: string (optional) The name of the user's application.
      server: string (optional) The name of the server to which a connection
          will be opened. Default value: 'www.google.com'.
      contact_list: string (optional) The name of the default contact list to
          use when no URI is specified to the methods of the service.
          Default value: 'default' (the logged in user's contact list).
      **kwargs: The other parameters to pass to gdata.service.GDataService
          constructor.
    """

    self.contact_list = contact_list
    gdata.service.GDataService.__init__(
        self, email=email, password=password, service='cp', source=source,
        server=server, additional_headers=additional_headers, **kwargs)

  def GetFeedUri(self, kind='contacts', contact_list=None, projection='full',
                 scheme=None):
    """Builds a feed URI.

    Args:
      kind: The type of feed to return, typically 'groups' or 'contacts'.
        Default value: 'contacts'.
      contact_list: The contact list to return a feed for.
        Default value: self.contact_list.
      projection: The projection to apply to the feed contents, for example
        'full', 'base', 'base/12345', 'full/batch'. Default value: 'full'.
      scheme: The URL scheme such as 'http' or 'https', None to return a
          relative URI without hostname.

    Returns:
      A feed URI using the given kind, contact list, and projection.
      Example: '/m8/feeds/contacts/default/full'.
    """
    contact_list = contact_list or self.contact_list
    if kind == 'profiles':
      contact_list = 'domain/%s' % contact_list
    prefix = scheme and '%s://%s' % (scheme, self.server) or ''
    return '%s/m8/feeds/%s/%s/%s' % (prefix, kind, contact_list, projection)

  def GetContactsFeed(self, uri=None):
    uri = uri or self.GetFeedUri()
    return self.Get(uri, converter=gdata.contacts.ContactsFeedFromString)

  def GetContact(self, uri):
    return self.Get(uri, converter=gdata.contacts.ContactEntryFromString)

  def CreateContact(self, new_contact, insert_uri=None, url_params=None,
                    escape_params=True):
    """Adds an new contact to Google Contacts.

    Args:
      new_contact: atom.Entry or subclass A new contact which is to be added to
                Google Contacts.
      insert_uri: the URL to post new contacts to the feed
      url_params: dict (optional) Additional URL parameters to be included
                  in the insertion request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful insert,  an entry containing the contact created
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server,
         'reason': HTTP reason from the server,
         'body': HTTP body of the server's response}
    """
    insert_uri = insert_uri or self.GetFeedUri()
    return self.Post(new_contact, insert_uri, url_params=url_params,
                     escape_params=escape_params,
                     converter=gdata.contacts.ContactEntryFromString)

  def UpdateContact(self, edit_uri, updated_contact, url_params=None,
                    escape_params=True):
    """Updates an existing contact.

    Args:
      edit_uri: string The edit link URI for the element being updated
      updated_contact: string, atom.Entry or subclass containing
                    the Atom Entry which will replace the contact which is
                    stored at the edit_url
      url_params: dict (optional) Additional URL parameters to be included
                  in the update request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful update,  a httplib.HTTPResponse containing the server's
        response to the PUT request.
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server,
         'reason': HTTP reason from the server,
         'body': HTTP body of the server's response}
    """
    return self.Put(updated_contact, self._CleanUri(edit_uri),
                    url_params=url_params,
                    escape_params=escape_params,
                    converter=gdata.contacts.ContactEntryFromString)

  def DeleteContact(self, edit_uri, extra_headers=None,
      url_params=None, escape_params=True):
    """Removes an contact with the specified ID from Google Contacts.

    Args:
      edit_uri: string The edit URL of the entry to be deleted. Example:
               '/m8/feeds/contacts/default/full/xxx/yyy'
      url_params: dict (optional) Additional URL parameters to be included
                  in the deletion request.
      escape_params: boolean (optional) If true, the url_parameters will be
                     escaped before they are included in the request.

    Returns:
      On successful delete,  a httplib.HTTPResponse containing the server's
        response to the DELETE request.
      On failure, a RequestError is raised of the form:
        {'status': HTTP status code from server,
         'reason': HTTP reason from the server,
         'body': HTTP body of the server's response}
    """
    return self.Delete(self._CleanUri(edit_uri),
                       url_params=url_params, escape_params=escape_params)

  def GetGroupsFeed(self, uri=None):
    uri = uri or self.GetFeedUri('groups')
    return self.Get(uri, converter=gdata.contacts.GroupsFeedFromString)

  def CreateGroup(self, new_group, insert_uri=None, url_params=None,
                  escape_params=True):
    insert_uri = insert_uri or self.GetFeedUri('groups')
    return self.Post(new_group, insert_uri, url_params=url_params,
        escape_params=escape_params,
        converter=gdata.contacts.GroupEntryFromString)

  def UpdateGroup(self, edit_uri, updated_group, url_params=None,
                  escape_params=True):
    return self.Put(updated_group, self._CleanUri(edit_uri),
                    url_params=url_params,
                    escape_params=escape_params,
                    converter=gdata.contacts.GroupEntryFromString)

  def DeleteGroup(self, edit_uri, extra_headers=None,
                  url_params=None, escape_params=True):
    return self.Delete(self._CleanUri(edit_uri),
                       url_params=url_params, escape_params=escape_params)

  def ChangePhoto(self, media, contact_entry_or_url, content_type=None, 
                  content_length=None):
    """Change the photo for the contact by uploading a new photo.

    Performs a PUT against the photo edit URL to send the binary data for the
    photo.

    Args:
      media: filename, file-like-object, or a gdata.MediaSource object to send.
      contact_entry_or_url: ContactEntry or str If it is a ContactEntry, this
                            method will search for an edit photo link URL and
                            perform a PUT to the URL.
      content_type: str (optional) the mime type for the photo data. This is
                    necessary if media is a file or file name, but if media
                    is a MediaSource object then the media object can contain
                    the mime type. If media_type is set, it will override the
                    mime type in the media object.
      content_length: int or str (optional) Specifying the content length is
                      only required if media is a file-like object. If media
                      is a filename, the length is determined using
                      os.path.getsize. If media is a MediaSource object, it is
                      assumed that it already contains the content length.
    """
    if isinstance(contact_entry_or_url, gdata.contacts.ContactEntry):
      url = contact_entry_or_url.GetPhotoEditLink().href
    else:
      url = contact_entry_or_url
    if isinstance(media, gdata.MediaSource):
      payload = media
    # If the media object is a file-like object, then use it as the file
    # handle in the in the MediaSource.
    elif hasattr(media, 'read'):
      payload = gdata.MediaSource(file_handle=media, 
          content_type=content_type, content_length=content_length)
    # Assume that the media object is a file name.
    else:
      payload = gdata.MediaSource(content_type=content_type, 
          content_length=content_length, file_path=media)
    return self.Put(payload, url)

  def GetPhoto(self, contact_entry_or_url):
    """Retrives the binary data for the contact's profile photo as a string.
    
    Args:
      contact_entry_or_url: a gdata.contacts.ContactEntry objecr or a string
         containing the photo link's URL. If the contact entry does not 
         contain a photo link, the image will not be fetched and this method
         will return None.
    """
    # TODO: add the ability to write out the binary image data to a file, 
    # reading and writing a chunk at a time to avoid potentially using up 
    # large amounts of memory.
    url = None
    if isinstance(contact_entry_or_url, gdata.contacts.ContactEntry):
      photo_link = contact_entry_or_url.GetPhotoLink()
      if photo_link:
        url = photo_link.href
    else:
      url = contact_entry_or_url
    if url:
      return self.Get(url, converter=str)
    else:
      return None

  def DeletePhoto(self, contact_entry_or_url):
    url = None
    if isinstance(contact_entry_or_url, gdata.contacts.ContactEntry):
      url = contact_entry_or_url.GetPhotoEditLink().href
    else:
      url = contact_entry_or_url
    if url:
      self.Delete(url)

  def GetProfilesFeed(self, uri=None):
    """Retrieves a feed containing all domain's profiles.

    Args:
      uri: string (optional) the URL to retrieve the profiles feed,
          for example /m8/feeds/profiles/default/full

    Returns:
      On success, a ProfilesFeed containing the profiles.
      On failure, raises a RequestError.
    """
    
    uri = uri or self.GetFeedUri('profiles')    
    return self.Get(uri,
                    converter=gdata.contacts.ProfilesFeedFromString)

  def GetProfile(self, uri):
    """Retrieves a domain's profile for the user.

    Args:
      uri: string the URL to retrieve the profiles feed,
          for example /m8/feeds/profiles/default/full/username

    Returns:
      On success, a ProfileEntry containing the profile for the user.
      On failure, raises a RequestError
    """
    return self.Get(uri,
                    converter=gdata.contacts.ProfileEntryFromString)

  def UpdateProfile(self, edit_uri, updated_profile, url_params=None,
                    escape_params=True):
    """Updates an existing profile.

    Args:
      edit_uri: string The edit link URI for the element being updated
      updated_profile: string atom.Entry or subclass containing
                    the Atom Entry which will replace the profile which is
                    stored at the edit_url.
      url_params: dict (optional) Additional URL parameters to be included
                  in the update request.
      escape_params: boolean (optional) If true, the url_params will be
                     escaped before they are included in the request.

    Returns:
      On successful update,  a httplib.HTTPResponse containing the server's
        response to the PUT request.
      On failure, raises a RequestError.
    """
    return self.Put(updated_profile, self._CleanUri(edit_uri),
                    url_params=url_params, escape_params=escape_params,
                    converter=gdata.contacts.ProfileEntryFromString)

  def ExecuteBatch(self, batch_feed, url,
                   converter=gdata.contacts.ContactsFeedFromString):
    """Sends a batch request feed to the server.
    
    Args:
      batch_feed: gdata.contacts.ContactFeed A feed containing batch
          request entries. Each entry contains the operation to be performed
          on the data contained in the entry. For example an entry with an
          operation type of insert will be used as if the individual entry
          had been inserted.
      url: str The batch URL to which these operations should be applied.
      converter: Function (optional) The function used to convert the server's
          response to an object. The default value is ContactsFeedFromString.
    
    Returns:
      The results of the batch request's execution on the server. If the
      default converter is used, this is stored in a ContactsFeed.
    """
    return self.Post(batch_feed, url, converter=converter)
  
  def ExecuteBatchProfiles(self, batch_feed, url,
                   converter=gdata.contacts.ProfilesFeedFromString):
    """Sends a batch request feed to the server.

    Args:
      batch_feed: gdata.profiles.ProfilesFeed A feed containing batch
          request entries. Each entry contains the operation to be performed
          on the data contained in the entry. For example an entry with an
          operation type of insert will be used as if the individual entry
          had been inserted.
      url: string The batch URL to which these operations should be applied.
      converter: Function (optional) The function used to convert the server's
          response to an object. The default value is
          gdata.profiles.ProfilesFeedFromString.

    Returns:
      The results of the batch request's execution on the server. If the
      default converter is used, this is stored in a ProfilesFeed.
    """
    return self.Post(batch_feed, url, converter=converter)

  def _CleanUri(self, uri):
    """Sanitizes a feed URI.

    Args:
      uri: The URI to sanitize, can be relative or absolute.

    Returns:
      The given URI without its http://server prefix, if any.
      Keeps the leading slash of the URI.
    """
    url_prefix = 'http://%s' % self.server
    if uri.startswith(url_prefix):
      uri = uri[len(url_prefix):]
    return uri

class ContactsQuery(gdata.service.Query):

  def __init__(self, feed=None, text_query=None, params=None,
      categories=None, group=None):
    self.feed = feed or '/m8/feeds/contacts/default/full'
    if group:
      self._SetGroup(group)
    gdata.service.Query.__init__(self, feed=self.feed, text_query=text_query,
        params=params, categories=categories)

  def _GetGroup(self):
    if 'group' in self:
      return self['group']
    else:
      return None

  def _SetGroup(self, group_id):
    self['group'] = group_id

  group = property(_GetGroup, _SetGroup, 
      doc='The group query parameter to find only contacts in this group')

class GroupsQuery(gdata.service.Query):

  def __init__(self, feed=None, text_query=None, params=None,
      categories=None):
    self.feed = feed or '/m8/feeds/groups/default/full'
    gdata.service.Query.__init__(self, feed=self.feed, text_query=text_query,
        params=params, categories=categories)


class ProfilesQuery(gdata.service.Query):
  """Constructs a query object for the profiles feed."""

  def __init__(self, feed=None, text_query=None, params=None,
               categories=None):
    self.feed = feed or '/m8/feeds/profiles/default/full'
    gdata.service.Query.__init__(self, feed=self.feed, text_query=text_query,
                                 params=params, categories=categories)
