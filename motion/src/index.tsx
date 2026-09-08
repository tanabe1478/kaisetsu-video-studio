import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {PrefixLesson} from './prefix';
import example from './example.json';
registerRoot(()=> <Composition id="PrefixChange" component={PrefixLesson} width={1280} height={720} fps={24} durationInFrames={954} defaultProps={example}/>);
