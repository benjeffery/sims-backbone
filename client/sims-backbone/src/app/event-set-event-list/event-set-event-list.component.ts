import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';

import { SamplingEventService } from '../typescript-angular-client/api/samplingEvent.service';

@Component({
  selector: 'app-event-set-event-list',
  templateUrl: './event-set-event-list.component.html',
  styleUrls: ['./event-set-event-list.component.scss']
})
export class EventSetEventListComponent implements OnInit {

  eventSetId: string;
  filter: string;

  constructor(private route: ActivatedRoute) { }

  ngOnInit() {
    this.route.paramMap.subscribe(pmap => {
      this.eventSetId = pmap.get('eventSetId');
    });
    this.filter = 'eventSet:' + this.eventSetId;
  }
}
