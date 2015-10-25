#pragma once

#include "pandabase.h"
#include "luse.h"
#include "datagramIterator.h"
#include "boundingBox.h"

#include <list>

class SGTriangleStrip;

// This class contains a whole dataset of triangle strips
class SGDataset {

    public:
        SGDataset();
        ~SGDataset();

        void read_bounds(DatagramIterator &dgi);
        void attach_strip(const SGTriangleStrip *strip);

        PT(BoundingBox) get_bounds();

    private:

        LVecBase3f _bb_min;
        LVecBase3f _bb_max;
        PT(BoundingBox) _bounds;
        list<const SGTriangleStrip*> _strips;

};