This is a <a target="_blank" href="https://nownownow.com/about">Now Page</a>, inspired
by <a target="_blank" href="https://sive.rs">Derek Sivers</a>.

{% set updated = getmtime('app/templates/main/main/now/\_now.md') * 1000 %}
*<time id="now-last-updated" data-last-updated="{{ updated }}"></time>*<br>
<small><time id="now-time-since"></time></small>

# What am I up to right now?

## Where is home currently?

**SF Bay Area.**

Taking a break from [subielife]({{ url_for\('main.subielife'\) }}) and currently back
in the bay! I plan to stay here for the foreseeable future as the pandemic plays out.

<div id="distance-apart" style="display: none;">
  <p><em>Psst...if you want to know how far apart we currently are, click the following
  button ;)</em></p>

  <button id="distance-apart__button" class="button--center">CLICK HERE...</button>
</div>

## What am I working on?

**Becoming a [{dev}athlete]({{ url_for\('main.devathlete'\)}}).**

Over the past months, I've been splitting my time 50-50 between coding and training
calisthenics.

On the coding side, after finishing my first non-personal project (an ecommerce website
for a friend's <a target="_blank" href="https://batch22bakery.com">bakery</a>), I moved
on to rebuilding this blog from scratch using Flask, PostgreSQL, and TypeScript.
Recently, I've been working on learning the D3.js library for data visualization and
also built my own [Buy Me a Coffee]({{ url_for\('main.support'\) }}) page using Stripe.

On the training front, I've switch my focus to achieving calisthenics skills as my
number one goal. Specifically, I am working on improving my one-arm pull-up and front
lever, while trying to unlock the straddle planche and handstand push-up.

## What else am I up to?

**Meditating and journaling.**

One of the most helpful courses I took back in early 2020 was <a target="_blank"
href="https://www.edbatista.com/the-art-of-self-coaching-public-course.html"> The Art of
Self-Coaching</a> by Ed Batista (an executive coach and teacher at Stanford University).
One of my biggest takeaways from the course was the benefits of having a regular
meditation and journaling practice. Since completing the course, I have been on a streak
of daily meditation and journaling. I have found the practice immensely calming and
intend to keep it up for the rest of my life.
