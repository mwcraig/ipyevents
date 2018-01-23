import {
  Application, IPlugin
} from '@phosphor/application';

import {
  Widget
} from '@phosphor/widgets';

import {
  IJupyterWidgetRegistry
 } from '@jupyter-widgets/base';

import {
  EventModel
} from './events';

import {
  JUPYTER_EXTENSION_VERSION
} from './version';

/**
 * The example plugin.
 */
const ipyeventsPlugin: IPlugin<Application<Widget>, void> = {
  id: 'ipyevents',
  requires: [IJupyterWidgetRegistry],
  activate: activateWidgetExtension,
  autoStart: true
};

export default ipyeventsPlugin;


/**
 * Activate the widget extension.
 */
function activateWidgetExtension(app: Application<Widget>, registry: IJupyterWidgetRegistry): void {
  registry.registerWidget({
    name: 'ipyevents',
    version: JUPYTER_EXTENSION_VERSION,
    exports: {
      EventModel: EventModel
    }
  });
}
