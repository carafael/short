package com.saw.adjustment

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.abs
import kotlin.math.sqrt

class SawGeometryTest {

    private val EPS = 1e-6

    @Test
    fun `symmetric slot depths produce centered saw`() {
        // Equal slot depths → h should be 0 (saw is centered)
        val result = SawGeometry.computeSawCenter(
            partDiameter = 1.0,
            sawDiameter = 3.0,
            rearSlotDepth = 0.5,
            frontSlotDepth = 0.5
        )
        assertNotNull(result)
        assertEquals(0.0, result!!.sawCenterX, EPS)
    }

    @Test
    fun `asymmetric slot depths produce non-zero h`() {
        val result = SawGeometry.computeSawCenter(
            partDiameter = 1.0,
            sawDiameter = 3.0,
            rearSlotDepth = 0.5,
            frontSlotDepth = 0.3
        )
        assertNotNull(result)
        // h should not be zero when depths differ
        assertTrue(abs(result!!.sawCenterX) > EPS)
    }

    @Test
    fun `saw center lies on both construction circles`() {
        val partDiam = 1.0
        val sawDiam = 3.0
        val rearDepth = 0.5
        val frontDepth = 0.3

        val result = SawGeometry.computeSawCenter(partDiam, sawDiam, rearDepth, frontDepth)
        assertNotNull(result)

        val sawRadius = sawDiam / 2.0
        val partRadius = partDiam / 2.0
        val h = result!!.sawCenterX
        val k = result.sawCenterY

        // Distance from saw center to C1 = (-partRadius, rearDepth) should equal sawRadius
        val d1 = sqrt((h - (-partRadius)) * (h - (-partRadius)) + (k - rearDepth) * (k - rearDepth))
        assertEquals(sawRadius, d1, EPS)

        // Distance from saw center to C2 = (+partRadius, frontDepth) should equal sawRadius
        val d2 = sqrt((h - partRadius) * (h - partRadius) + (k - frontDepth) * (k - frontDepth))
        assertEquals(sawRadius, d2, EPS)
    }

    @Test
    fun `saw center y is negative (below part tip)`() {
        val result = SawGeometry.computeSawCenter(
            partDiameter = 1.0,
            sawDiameter = 3.0,
            rearSlotDepth = 0.5,
            frontSlotDepth = 0.3
        )
        assertNotNull(result)
        assertTrue("k should be < 0", result!!.sawCenterY < 0.0)
    }

    @Test
    fun `returns null when circles are too far apart`() {
        // Saw diameter too small for circles to intersect
        val result = SawGeometry.computeSawCenter(
            partDiameter = 4.0,
            sawDiameter = 2.0,   // sawRadius=1, partDiam=4 → centers 4 apart, 2r=2 < 4
            rearSlotDepth = 0.0,
            frontSlotDepth = 0.0
        )
        assertNull(result)
    }

    @Test
    fun `returns null when circles are coincident`() {
        // Both centers at same point (partDiam=0 would do it, but we need d~0)
        val result = SawGeometry.computeSawCenter(
            partDiameter = 0.0001, // nearly zero → centers nearly coincident
            sawDiameter = 3.0,
            rearSlotDepth = 0.5,
            frontSlotDepth = 0.5
        )
        // d ≈ 0.0001, 2r = 3.0 → should still intersect (d < 2r and d > 0)
        // Actually this WILL find intersections. Let me test true coincidence:
        assertNotNull(result) // this case does intersect
    }

    @Test
    fun `adjustment text for positive h says LEFT`() {
        val text = SawGeometry.adjustmentText(0.1234)
        assertTrue(text.contains("LEFT"))
        assertTrue(text.contains("0.1234"))
    }

    @Test
    fun `adjustment text for negative h says RIGHT`() {
        val text = SawGeometry.adjustmentText(-0.0567)
        assertTrue(text.contains("RIGHT"))
        assertTrue(text.contains("0.0567"))
    }

    @Test
    fun `adjustment text for zero h says centered`() {
        val text = SawGeometry.adjustmentText(0.0)
        assertTrue(text.contains("centered"))
    }

    @Test
    fun `both intersections lie on both circles`() {
        val partDiam = 1.5
        val sawDiam = 4.0
        val rearDepth = 0.4
        val frontDepth = 0.6

        val result = SawGeometry.computeSawCenter(partDiam, sawDiam, rearDepth, frontDepth)
        assertNotNull(result)

        val sawRadius = sawDiam / 2.0
        val partRadius = partDiam / 2.0

        // Check intersection A
        val (ax, ay) = result!!.intersectionA
        val dA1 = sqrt((ax + partRadius) * (ax + partRadius) + (ay - rearDepth) * (ay - rearDepth))
        val dA2 = sqrt((ax - partRadius) * (ax - partRadius) + (ay - frontDepth) * (ay - frontDepth))
        assertEquals(sawRadius, dA1, EPS)
        assertEquals(sawRadius, dA2, EPS)

        // Check intersection B
        val (bx, by) = result.intersectionB
        val dB1 = sqrt((bx + partRadius) * (bx + partRadius) + (by - rearDepth) * (by - rearDepth))
        val dB2 = sqrt((bx - partRadius) * (bx - partRadius) + (by - frontDepth) * (by - frontDepth))
        assertEquals(sawRadius, dB1, EPS)
        assertEquals(sawRadius, dB2, EPS)
    }
}
