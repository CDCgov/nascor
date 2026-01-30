# nascor

nascor is a tool for manipulating ages and age ranges. The name is from [the Latin](https://en.wiktionary.org/wiki/nascor#Latin).

In nascor, each _age_ is a period of time, from age zero (i.e., birth) to some later time, defined in years, months, or weeks. We can easily compare ages of the same unit, but in general, we cannot compare ages of different units:

- One year equals 12 months.
- Zero of anything equals zero of anything else.
- Otherwise, there is no comparison: a month is not 4 weeks, nor is a year 52 weeks.

An _age range_ is a pair of ages (like 0-18 years) or a single age with no upper limit (like 65+ years). nascor can parse certain string representations of age ranges.

Note that "age" is often loosely used to refer to an age _range_. For example, "1 year olds" are those individuals between 1.0 and 2.0 years of age. This distinction helps clarify that "0-<1 years" refers to 0.0 to 1.0 years while "0-1 years" refers to individuals from 0.0 to 2.0 years.
