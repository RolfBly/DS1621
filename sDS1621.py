#! /usr/bin/env python
# -*- coding: utf-8 -*-

# workaround for GPIO (I2C bus) needing root rights

import subprocess

subprocess.call(['sudo', './ds1621.py'])