import calendar
import datetime
from dateable import kalends

try:
    from Products.Five.browser.pagetemplatefile import \
         ZopeTwoPageTemplateFile as PageTemplateFile
except ImportError:
    from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from zope.component import queryMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from Products.CMFPlone.PloneBatch import Batch


class ILOEventListingView (object):
    """
    """

    eventlist = PageTemplateFile('events.pt')    

    def _getEventList(self, start=None, stop=None):
        provider = kalends.IEventProvider(self.context)
        now = datetime.datetime.now()
        events = list(provider.getOccurrences(start=start, stop=stop, 
                                             **self.request.form))
        events.sort()
        months = []
        month_info = []
        old_month_year = None
        for event in events:
            start = event.start
            end = event.end
            month = str(start.month)
            year = str(start.year)
            month_year = year+month
            if month_year != old_month_year:
                old_month_year = month_year
                if month_info:
                    months.append(month_info)
                month_info = {'month': start.month,
                              'year': start.year,
                              'month_name': start.strftime("%B"),
                              'events': []}
            event_dict = {'event': event,
                          'day': start.day,
                          'month' : start.month,
                          'month_name': start.strftime('%b'),
                          'year' : start.year,
                          'day_end' : end.day,
                          'month_end' : end.month,
                          'month_end_name': end.strftime('%b'),
                          'year_end' : end.year, 
                          'title': event.title,
                          'description': event.description,
                          'location': event.location,
                          'url': event.url,
                          }
            month_info['events'].append(event_dict)

        if month_info:
            months.append(month_info)
            
        return months

    def current(self):
        return self.__name__

    def upcomingEvents(self):
        """Show all upcoming events"""
        now = datetime.datetime.now()
        months = list(self._getEventList(start=now))
        b_start = self.request.get('b_start', 0)
        batch = Batch(months, 2, int(b_start), orphan=0)
        return self.eventlist(months=batch, show_past=False)

    def pastEvents(self):
        """Show all past events"""
        now = datetime.datetime.now()
        months = list(reversed(self._getEventList(stop=now)))
        b_start = self.request.get('b_start', 0)
        batch = Batch(months, 2, int(b_start), orphan=0)
        return self.eventlist(months=batch, show_past=True)

    def allEvents(self):
        """Show all events"""
        now = datetime.datetime.now()
        months = list(reversed(self._getEventList()))
        b_start = self.request.get('b_start', 0)
        batch = Batch(months, 2, int(b_start), orphan=0)
        return self.eventlist(months=batch, show_past=True)

    def render_filter(self):
        provider = queryMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, 'eventfilter')
        if provider is None:
            return ''
        provider.update()
        return provider.render()
