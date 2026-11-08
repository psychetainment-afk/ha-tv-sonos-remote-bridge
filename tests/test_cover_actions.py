"""Evaluate actual Green YAML against simulated cover states; no device calls."""
import unittest
import yaml
from jinja2 import Environment

config = yaml.safe_load(COLOR_YAML)
green = next(a for a in config['automation'] if a['id']=='tv_remote_green_cover_position')

class CoverTests(unittest.TestCase):
    def press(self, state, position, next_open):
        values={'cover.YOUR_LIVING_ROOM_COVER':state,'input_boolean.tv_remote_cover_next_open':next_open}
        env=Environment()
        env.globals.update(states=lambda entity: values.get(entity,'unknown'),
            is_state=lambda entity,value: values.get(entity)==value,
            state_attr=lambda entity,attribute: position)
        def condition(template):
            return env.from_string(template).render().strip().lower()=='true'
        actions=[]
        def execute(sequence):
            for step in sequence:
                if 'choose' in step:
                    branch=next((b['sequence'] for b in step['choose'] if condition(b['conditions'])),step.get('default',[]))
                    execute(branch)
                else:
                    action=step['action']
                    if action.startswith('input_boolean.'):
                        values['input_boolean.tv_remote_cover_next_open']='on' if action.endswith('turn_on') else 'off'
                    else:
                        actions.append((action,step.get('data',{})))
        if all(condition(c['value_template']) for c in green['conditions']):
            execute(green['actions'])
        return actions,values['input_boolean.tv_remote_cover_next_open']

    def test_top_goes_only_to_half(self):
        actions,remembered=self.press('open',100,'off')
        self.assertEqual(actions,[('cover.set_cover_position',{'position':50})])
        self.assertEqual(remembered,'on')

    def test_moving_press_stops_in_both_directions(self):
        for state,remembered in [('closing','on'),('opening','off')]:
            with self.subTest(state=state):
                self.assertEqual(self.press(state,75,'off'),([('cover.stop_cover',{})],remembered))

    def test_next_press_reverses_after_stop(self):
        self.assertEqual(self.press('open',75,'on')[0],[('cover.open_cover',{})])
        self.assertEqual(self.press('open',75,'off')[0],[('cover.set_cover_position',{'position':50})])

    def test_lower_limit_always_opens(self):
        for position in [0,40,50]:
            self.assertEqual(self.press('open',position,'off')[0],[('cover.open_cover',{})])

    def test_unavailable_or_missing_position_or_helper_does_nothing(self):
        for state,position,helper in [('unavailable',75,'off'),('open',None,'off'),('open',75,'unknown')]:
            self.assertEqual(self.press(state,position,helper)[0],[])
